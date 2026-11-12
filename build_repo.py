import gzip, hashlib, os, shutil, email.utils, time

ROOT = os.path.dirname(os.path.abspath(__file__))
DEB_NAME = "AppSyncUnified-rootless.deb"
DEB_SRC = os.path.join(os.environ["USERPROFILE"], "Desktop", DEB_NAME)
DEB_DST = os.path.join(ROOT, "debs", DEB_NAME)

os.makedirs(os.path.join(ROOT, "debs"), exist_ok=True)
shutil.copyfile(DEB_SRC, DEB_DST)

data = open(DEB_DST, "rb").read()
size = len(data)
md5 = hashlib.md5(data).hexdigest()
sha256 = hashlib.sha256(data).hexdigest()

stanza = f"""Package: ai.akemi.appsyncunified
Name: AppSync Unified
Version: 116.0
Architecture: iphoneos-arm64
Description: Enables the ability to install unsigned/fakesigned iOS applications.
Section: Tweaks
Maintainer: Karen <karen@akemi.ai>
Author: Karen, Linus Yang <karen@akemi.ai>
Depends: firmware (>= 5.0), mobilesubstrate (>= 0.9.5100)
Conflicts: us.hackulo.appsync50, us.hackulo.appsync50plus, com.hackyouriphone.appsync7, com.teiron.ppsync, appsync50plus2.25pp, com.linusyang.appsync, com.sull.appsyncunified, com.sull.appsyncunifiedbeta, com.xsellize.appsync50, com.xsellize.appsync50plus, appsync50plus.178, appsync50plus2.178, cydia.net.angelxwind.appsyncunified, com.ifucker.appsync, com.sexyphonetech.appsyncunified, appsyncunifiedofficial, org.digbick.asufixed, technology.goated.appsync, technology.goated.appsyncunified, ellekit (< 1.1)
Replaces: us.hackulo.appsync50, net.angelxwind.appsyncunified
Provides: appsync, net.angelxwind.appsyncunified
Installed-Size: 668
Homepage: https://github.com/akemin-dayo/AppSync
Depiction: https://github.com/akemin-dayo/AppSync
Filename: debs/{DEB_NAME}
Size: {size}
MD5sum: {md5}
SHA256: {sha256}
"""

packages = stanza.replace("\n", "\n").encode("utf-8")
if not packages.endswith(b"\n"):
    packages += b"\n"

def write(path, blob):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(blob)

def hashes(blob):
    return hashlib.md5(blob).hexdigest(), hashlib.sha256(blob).hexdigest()

gz = gzip.compress(packages, mtime=0)

# flat layout
write("Packages", packages)
write("Packages.gz", gz)

date = email.utils.formatdate(time.time(), usegmt=True)

def release(components):
    md5p, shap = hashes(packages)
    md5g, shag = hashes(gz)
    comp = f"Components: {components}\n" if components else ""
    text = (
        "Origin: M4APlayer Mirror\n"
        "Label: M4APlayer Mirror\n"
        "Suite: stable\n"
        "Version: 1.0\n"
        "Codename: ios\n"
        f"Date: {date}\n"
        "Architectures: iphoneos-arm64\n"
        f"{comp}"
        "Description: Mirror of AppSync Unified 116.0 (rootless) for jailbroken iOS.\n"
        "MD5Sum:\n"
        f" {md5p} {len(packages)} Packages\n"
        f" {md5g} {len(gz)} Packages.gz\n"
        "SHA256:\n"
        f" {shap} {len(packages)} Packages\n"
        f" {shag} {len(gz)} Packages.gz\n"
    )
    return text.encode("utf-8")

# Sileo requires a "Components" key even for flat repos (RepoManager.swift:651),
# so the root Release must declare it; the source itself stays flat (suite "").
write("Release", release("main"))

for codename in ("ios", "stable"):
    base = f"dists/{codename}"
    write(f"{base}/Release", release("main"))
    write(f"{base}/main/binary-iphoneos-arm64/Packages", packages)
    write(f"{base}/main/binary-iphoneos-arm64/Packages.gz", gz)

print("size", size, "md5", md5, "sha256", sha256)
for dirpath, _, files in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for f in sorted(files):
        p = os.path.join(dirpath, f)
        print(" ", os.path.relpath(p, ROOT), os.path.getsize(p))
