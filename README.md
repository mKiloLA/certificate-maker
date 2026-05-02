# Certificate Maker

This program starts a GUI that takes a Zoom attendence file and master CLE list and outputs certificates of attendence.

## Installation (macOS)

* Download the latest release from the [releases tab](https://github.com/mKiloLA/certificate-maker/releases).
* Move the app to the Applications folder and attempt to run it.
  * Since this app is not signed by an Apple Developer account, step 2 will fail.
* To bypass this, go into System Settings -> Privacy & Security -> Security and click "Open Anyway" for the CertificateMaker app.
  * This should only be required once, but sometimes you have to do it twice.
* copy the [Certificates](Certificates) file to your home directory. This is where the application will find the certificate template, output the new certificates, and write log files.
* In [Certificates/References](Certificates/References), add your Outlook email address and password to the `Outlook.txt` file.

## Build from Source

The intended use of the program is through an application created by pyinstaller using the following command in the project root directory:

```bash
pyinstaller --noconfirm --clean CertificateMaker.spec
```

Optionally, you can build the source with the following code:

If you want to change the icon, do the following from root with an icon named `icon.png`.

```bash
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
cp icon.png icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

Then, run the following command to build the app:

```bash
pyinstaller certificate_maker/__main__.py --name CertificateMaker --paths . --onedir --noconfirm --noconsole --icon=icon.icns --collect-all selenium --collect-all certifi
```

or build from the spec file:

```bash
pyinstaller --noconfirm --clean CertificateMaker.spec
```

Optionally, if you want to create an installer:

```bash
brew install create-dmg
create-dmg --volname "CertificateMaker" --window-size 1200 400 --app-drop-link 450 200 "CertificateMaker.dmg" "dist/CertificateMaker.app"
```

After running the command, there are three more steps:

1. copy the [Certificates](Certificates) file to your home directory. This is where the application will find the certificate template, output the new certificates, and write log files.
2. In [Certificates/References](Certificates/References), add your Outlook email address and password to the `Outlook.txt` file.
3. Go into the `dist` folder that pyinstaller created and move the `CertificateMaker.app` file to your Applications folder.

The app is now ready to be used. Note that the app is relatively slow to launch. It may seem that it crashes immediately, but it is just loading.
