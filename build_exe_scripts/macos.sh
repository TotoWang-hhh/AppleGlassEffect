echo Many thanks to CodeCrafter-TL for developing and testing of this script!
cd ..
echo Building executables...
pyinstaller -i ./icons/icon2.ico --noconfirm --log-level=ERROR -w demo_launcher.py
echo Demos built
echo Copying files...
mkdir "./finals/"
cp -r "./dist/demo_launcher.app" "./finals/Lauch Demos.app"
echo Demo apps copied
mkdir "./finals/icons/"
cp -r "./icons/" "./finals/icons/"
mkdir "./finals/test_imgs/"
cp -r "./test_imgs/" "./finals/test_imgs/"
echo Icons and images copyed
cp "./README.md" "./finals"
cp "./liquidglass.py" "./finals"
echo Instruction and core copyed
echo Cleaning up...
rm -r ./dist/
rm -r ./build/
echo "===================="
echo Build completed