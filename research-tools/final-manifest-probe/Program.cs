using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using TACTLib.Core.Product.Tank;
using TACTLib.Core.Product.Tank.CMF;

// Read-only manifest decoder. Input must already match the original ROOT CKey.
// Output contains GUID/size/content-key metadata only, never decoded assets or
// authentication information. Crypto comes from the exact external provider.
if (args.Length != 3) {
    Console.Error.WriteLine("final-manifest-probe CMF_FILE EXPECTED_CONTENT_MD5 OUTPUT_TSV");
    return 2;
}
try {
    var input = new FileInfo(args[0]);
    if (input.Length < 48 || input.Length > 128 * 1024 * 1024) throw new InvalidDataException("Manifest size limit");
    byte[] blob = File.ReadAllBytes(input.FullName);
    if (!MD5.HashData(blob).AsSpan().SequenceEqual(Convert.FromHexString(args[1]))) throw new InvalidDataException("Manifest content hash mismatch");
    uint U32(int offset) => BinaryPrimitives.ReadUInt32LittleEndian(blob.AsSpan(offset, 4));
    uint build = U32(0), count = U32(32), entries = U32(40), magic = U32(44);
    if (build != 104319 || count > 2_000_000 || entries > 2_000_000) throw new InvalidDataException("Requires bounded final-OW1 manifest");
    bool encrypted = magic >> 8 == 0x636d66;
    if (!encrypted && (magic & 0xffffff) != 0x666d63) throw new InvalidDataException("Manifest magic mismatch");
    byte[] body = blob[48..];
    if (encrypted) {
        if (body.Length % 16 != 0) throw new InvalidDataException("Encrypted manifest block bounds");
        var provider = new ProCMF_104319();
        var header = new ContentManifestFile.CMFHeader { m_buildVersion = build };
        byte[] digest = SHA1.HashData(Encoding.ASCII.GetBytes(input.Name));
        using var aes = Aes.Create();
        aes.Key = provider.Key(header, 32); aes.IV = provider.IV(header, digest, 16);
        aes.Mode = CipherMode.CBC; aes.Padding = PaddingMode.None;
        body = aes.DecryptCbc(body, aes.IV, PaddingMode.None);
    }
    long tableEnd = (long)entries * 20 + (long)count * 29;
    // The original reader ignores the final AES padding block. An exactly
    // block-aligned table can still carry sixteen padding bytes.
    if (tableEnd > body.Length || body.Length - tableEnd > 16) throw new InvalidDataException("Manifest table bounds");
    if (entries > 0 && BinaryPrimitives.ReadUInt32LittleEndian(body.AsSpan(0,4)) != 1) throw new InvalidDataException("Decoded entry/IV check failed");
    // Validate all records before creating any output.
    ulong previous = 0;
    for (int n = 0; n < count; n++) {
        int offset = checked((int)entries * 20 + n * 29);
        ulong guid = BinaryPrimitives.ReadUInt64LittleEndian(body.AsSpan(offset,8));
        if (n > 0 && guid <= previous) throw new InvalidDataException("Decoded GUID ordering check failed");
        previous = guid;
    }
    using (var output = new StreamWriter(new FileStream(args[2], FileMode.CreateNew, FileAccess.Write))) {
        output.WriteLine("guid\tbytes\tcontent_md5");
        for (int n = 0; n < count; n++) {
            int offset = checked((int)entries * 20 + n * 29);
            ulong guid = BinaryPrimitives.ReadUInt64LittleEndian(body.AsSpan(offset,8));
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(body.AsSpan(offset+8,4));
            output.WriteLine($"{guid:x16}\t{size}\t{Convert.ToHexString(body.AsSpan(offset+13,16)).ToLowerInvariant()}");
        }
    }
    Console.WriteLine(JsonSerializer.Serialize(new { build, encrypted, entries, assets = count, source_md5_verified = true, metadata_only = true }));
    return 0;
} catch (Exception error) {
    Console.Error.WriteLine(error.Message);
    return 1;
}
