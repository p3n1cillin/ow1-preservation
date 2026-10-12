// Minimal host for TACTLib's externally linked, MIT-licensed 104319 provider.
namespace TACTLib.Core.Product.Tank {
    public interface ICMFEncryptionProc {
        byte[] Key(ContentManifestFile.CMFHeader header, int length);
        byte[] IV(ContentManifestFile.CMFHeader header, byte[] digest, int length);
    }
    public static class ContentManifestFile {
        public struct CMFHeader { public uint m_buildVersion; }
    }
    public static class ManifestCryptoHandler {
        public const uint SHA1_DIGESTSIZE = 20;
        public enum TACTProduct { Overwatch }
        [AttributeUsage(AttributeTargets.Class)]
        public class ManifestCryptoAttribute : Attribute {
            public bool AutoDetectVersion;
            public TACTProduct Product;
        }
        public static int SignedMod(long a, long b) {
            int x = unchecked((int)a), y = unchecked((int)b);
            if (y <= 0) throw new InvalidDataException("Invalid provider modulus");
            int result = x % y;
            return result < 0 ? result + y : result;
        }
    }
}
