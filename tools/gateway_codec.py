"""Bounded compact binary fields for the demonstrated 104319 lobby messages.

Schemas contain numeric interface descriptors only. Keys are native field
offsets, not guessed semantic names. No account or native image data is bundled.
"""
import json
import struct

FORMATS = {1:'b', 2:'B', 3:'B', 4:'h', 5:'H', 6:'i', 7:'I', 8:'Q', 9:'q', 10:'f', 11:'d'}
BLOB = 15  # u32 length + raw bytes (native writer 0x005668e0, reader case 15)
MAX_BODY = 4096
MAX_ITEMS = 1024
MAX_SCHEMA_FILE = 262144
MAX_SCHEMA_FIELDS = 4096
MAX_SCHEMA_MESSAGES = 64


def load_messages(path):
    with open(path, 'rb') as source:
        data = source.read(MAX_SCHEMA_FILE+1)
    if len(data) > MAX_SCHEMA_FILE:
        raise ValueError('message schema size bound')
    document = json.loads(data)
    if not isinstance(document, dict) or document.get('build') != 104319:
        raise ValueError('message schema build')
    messages = document.get('messages')
    if not isinstance(messages, list) or not 0 < len(messages) <= MAX_SCHEMA_MESSAGES:
        raise ValueError('message schema count')
    budget = [MAX_SCHEMA_FIELDS]
    def validate(fields, depth=0):
        if not isinstance(fields,list) or len(fields)>128 or depth>8:
            raise ValueError('field schema depth/count')
        offsets = set()
        for field in fields:
            budget[0] -= 1
            if not isinstance(field,dict) or budget[0]<0:
                raise ValueError('field schema bound')
            kind,offset,width,count = (field.get(key) for key in ('kind','offset','width','count'))
            if any(type(value) is not int for value in (kind,offset,width,count)) or kind not in (0,*FORMATS,12,13,14,BLOB):
                raise ValueError('unsupported field schema types')
            if not 0<=offset<=65536 or offset in offsets or not 0<width<=65536 or not -1<=count<=MAX_ITEMS:
                raise ValueError('field schema bounds/duplicate offset')
            offsets.add(offset)
            if kind==14: validate(field.get('fields'),depth+1)
    result = {}
    for message in messages:
        if not isinstance(message,dict): raise ValueError('message schema record')
        schema,mid = message.get('schema_hash'),message.get('message_id')
        if type(schema) is not int or type(mid) is not int or not 0<schema<=0xffffffff or not 0<mid<65536 or (schema,mid) in result:
            raise ValueError('message schema identity')
        validate(message.get('fields'))
        result[schema,mid] = message['fields']
    return result


class Reader:
    def __init__(self, data):
        if not 0<=len(data)<=MAX_BODY: raise ValueError('message body size bound')
        self.data, self.pos, self.bits, self.mask = data,0,0,0

    def take(self, count):
        self.mask = 0  # non-bit operations align to the next byte
        if count>len(self.data)-self.pos: raise ValueError('truncated compact field')
        start=self.pos;self.pos+=count
        return self.data[start:self.pos]

    def scalar(self, field):
        kind=field['kind']
        if kind==0:
            if not self.mask:
                self.bits=self.take(1)[0];self.mask=1
            value=bool(self.bits&self.mask)
            self.mask=(self.mask<<1)&255
            return value
        if kind in FORMATS:
            fmt='<'+FORMATS[kind]
            return struct.unpack(fmt,self.take(struct.calcsize(fmt)))[0]
        if kind in (12,13):
            self.mask=0
            end=self.data.find(b'\0',self.pos)
            if end<0: raise ValueError('unterminated compact string')
            value=self.take(end-self.pos+1)
            return value[:-1]
        if kind==14: return self.fields(field['fields'])
        if kind==BLOB:
            size=struct.unpack('<I',self.take(4))[0]
            if size>len(self.data)-self.pos: raise ValueError('compact blob length bound')
            return bytes(self.take(size))
        raise ValueError('unsupported compact kind')

    def fields(self, fields):
        result={}
        for field in fields:
            count=field['count']
            if count:
                if count==-1: count=struct.unpack('<I',self.take(4))[0]
                if count>MAX_ITEMS or count>8*(len(self.data)-self.pos):
                    raise ValueError('compact array count bound')
                result[field['offset']]=[self.scalar(field) for _ in range(count)]
            else: result[field['offset']]=self.scalar(field)
        return result


def decode(fields, body):
    reader=Reader(body)
    result=reader.fields(fields)
    if reader.pos!=len(body): raise ValueError('trailing compact message bytes')
    return result


class Writer:
    def __init__(self): self.data=bytearray();self.mask=0
    def put(self,value):
        self.mask=0
        if len(self.data)+len(value)>MAX_BODY: raise ValueError('message body size bound')
        self.data.extend(value)
    def scalar(self,field,value):
        kind=field['kind']
        if kind==0:
            if type(value) is not bool: raise ValueError('compact bool type')
            if not self.mask: self.put(b'\0');self.mask=1
            if value:self.data[-1]|=self.mask
            self.mask=(self.mask<<1)&255
        elif kind in FORMATS:
            if (type(value) is not float if kind in (10,11) else type(value) is not int):
                raise ValueError('compact number type')
            try:self.put(struct.pack('<'+FORMATS[kind],value))
            except struct.error as error:raise ValueError('compact integer bound') from error
        elif kind in (12,13):
            if not isinstance(value,bytes) or b'\0' in value:raise ValueError('compact string type/NUL')
            self.put(value+b'\0')
        elif kind==14:self.fields(field['fields'],value)
        elif kind==BLOB:
            if not isinstance(value,bytes):raise ValueError('compact blob type')
            self.put(struct.pack('<I',len(value))+value)
        else:raise ValueError('unsupported compact kind')
    def fields(self,fields,values):
        if not isinstance(values,dict) or values.keys()-{f['offset'] for f in fields}:
            raise ValueError('compact record fields')
        for field in fields:
            kind,count=field['kind'],field['count']
            default={} if kind==14 else False if kind==0 else b'' if kind in (12,13,BLOB) else 0.0 if kind in (10,11) else 0
            # Omitted arrays: empty when variable-length, zero items when fixed-size.
            value=values.get(field['offset'],([] if count==-1 else [default]*count) if count else default)
            if count:
                if not isinstance(value,list) or len(value)>MAX_ITEMS or (count>0 and len(value)!=count):
                    raise ValueError('compact array size/type')
                if count==-1:self.put(struct.pack('<I',len(value)))
                for item in value:self.scalar(field,item)
            else:self.scalar(field,value)


def encode(fields, values):
    writer=Writer();writer.fields(fields,values)
    return bytes(writer.data)
