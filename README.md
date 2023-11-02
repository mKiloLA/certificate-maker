# Certificate Maker

This program starts a GUI that takes a Zoom attendence file and master CLE list and outputs certificates of attendence.

## Installation

The intended use of the program is through an application created by pyinstaller using the following command in the project root directory:

```bash
pyinstaller --noconfirm --clean CertificateMaker.spec
```

Optionally, you can build the source with the following code:

```bash
pyinstaller certificate_maker/__main__.py --name CertificateMaker --paths . --onefile --noconfirm --noterminal
```

After running the command, there are two more steps:

1. copy the [Certificates](Certificates) file to your home directory. This is where the application will find the certificate template, output the new certificates, and write log files.
2. Go into the `dist` folder that pyinstaller created and move the `CertificateMaker.app` file to your Applications folder.

The app is now ready to be used. Note that the app is relatively slow to launch. It may seem that it crashes immediately, but it is just loading.

## Usage

Application for taking in a csv and making an attendence certificate.
