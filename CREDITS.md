# Credits and third-party references

This project is based on [Prometheus](https://github.com/saturn-xvi/prometheus) (see README.md and LICENSE).

## Overwatch 1.74 lobby server (Boi-027)

Some lobby behaviour implemented here follows the observations published by the MIT-licensed
[Boi-027/overwatch-1.74-lobby-server](https://github.com/Boi-027/overwatch-1.74-lobby-server),
an independent project for the same client build:

* the matchmaking queue reply order 44201 (queue entry echoing the request key), 44202 (queue end,
  reason 1 = popped) and then 20600;
* the leaver thresholds sent in 20813 at login (0, 20, 0.3, 0.2).

No code or client-derived data files were copied from that project; the message layouts used here are
exported from the client's own descriptor tables. Its license notice:

    MIT License
    Copyright (c) 2026 Arlecchino

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
    associated documentation files (the "Software"), to deal in the Software without restriction,
    including without limitation the rights to use, copy, modify, merge, publish, distribute,
    sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
    NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
    OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
