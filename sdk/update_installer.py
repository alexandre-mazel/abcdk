# v0.6

import abcdk.filetools as filetools
import abcdk.naoqitools as naoqitools

import shutil
import time

def getAbcdkVersion( strLibPath ):
    import abcdk.filetools as filetools
    import abcdk.stringtools as stringtools
    strFile = strLibPath + "/abcdk/__init__.py";
    enclosedFileData = filetools.getFileContents( strFile );
    nPick = enclosedFileData.find( "__version__" );
    if( nPick == -1 ):
        print( "INF: LifeData.getFileVersion: no version number found in %s (file size: %d)" % ( strFile, len( enclosedFileData ) ) );
        return "0.0";
    strVersion = stringtools.findBetween( enclosedFileData[nPick:], "'", "'" ); # look for string contents between ' and '
    print( "strVersion: '%s'" % str( strVersion ) );
    return strVersion;
# getAbcdkVersion - end


import zipfile

strFolderToIgnore = "abcdk/data/wav/tracker";

# we create two behaviors one in old format "folder" and one using the new one "exploded pml"
filetools.copyDirectory( "abcdk/", "installer/abcdk", ".pyc" );
filetools.copyDirectory( "abcdk/", "installer_pml/abcdk", ".pyc" );
#filetools.removeDirectory( "installer/abcdk/data/wav/tracker" );
shutil.rmtree( "installer/" + strFolderToIgnore );
shutil.rmtree( "installer_pml/" + strFolderToIgnore );

for strVersion in ["", "_1_12", "_1_14", "_1_17", "_1_18", "_1_22", "_1_22_2", "_1_22_3", "_2_0_3"]: # no one is using 1.16 anymore !  (nor 1.10)
    strArcName = "abcdk_installer%s.zip" % strVersion;
    print( "\n**** Creating zip archive %s" % strArcName );
    zipFile = zipfile.ZipFile( strArcName, "w", compression = zipfile.ZIP_DEFLATED );
    filetools.addFolderToZip( zipFile, "abcdk/", strFileTemplateToIgnore = ".pyc", astrFolderToIgnore = [strFolderToIgnore] );

    # add library
    #~ zipFile.write( "installer/behavior.xar", "behavior.xar" );
    strLibPath = "../../appu_modules/compiled_lib/";
    if( strVersion == "" ):
        filetools.addFolderToZip( zipFile, strLibPath, bStoreFullPath = False, strFileTemplateToMatch = strVersion );
    else:
        # find for each library the better version
        for strLibraryName in [ "libusagesound.so", "libusageubi.so", "libusagevision.so", "libusage.so" ]:
            strGoodLibName = naoqitools.findLibraryNameForVersion( strLibPath + strLibraryName, strVersion[1:].replace( "_", "." ) );
            if( strGoodLibName != "" ):
                strOnlyFilename = strGoodLibName.rsplit( "/", 1 )[1];
                zipFile.write( strGoodLibName, strOnlyFilename );
            
        # add from developer program (only in versionned zip)
        strSpecificPath = "../../../dp/datamatrix/compiled_lib/";
        strLibraryName = "libdatamatrix.so";
        strGoodLibName = naoqitools.findLibraryNameForVersion( strSpecificPath + strLibraryName, strVersion[1:].replace( "_", "." ) );
        if( strGoodLibName != "" ):
            strOnlyFilename = strGoodLibName.rsplit( "/", 1 )[1];
            zipFile.write( strGoodLibName, strOnlyFilename );
            
        # add from developer program (only in versionned zip)
        strSpecificPath = "../../../dp/haarextractor/compiled_lib/";
        strLibraryName = "libhaar_extractor.so";
        strGoodLibName = naoqitools.findLibraryNameForVersion( strSpecificPath + strLibraryName, strVersion[1:].replace( "_", "." ) );
        if( strGoodLibName != "" ):
            strOnlyFilename = strGoodLibName.rsplit( "/", 1 )[1];
            zipFile.write( strGoodLibName, strOnlyFilename );            
        

    if( strVersion < "_1_14" ):
        filetools.addFolderToZip( zipFile, "../library/application/behaviors/", bStoreFullPath = False, strSpecificDstPath = "./behaviors/" );

    zipFile.write( "installer/behavior.xar", "behavior.xar" );
    zipFile.write( "installer/.metadata", ".metadata" );
        
    
    zipFile.close();

print( "\n**** Creating version file 'abcdk_installer_version.txt'" );

strCurrentVersion = getAbcdkVersion( "." );
file = open( "abcdk_installer_version.txt", "wt" );
file.write( strCurrentVersion );
file.close();

print( "\n**** Now, if you're really proud of your version, you should download it to studio.aldebaran-robotics.com, sth like:" );
print( "scp abcdk_installer*.* amazel@studio.aldebaran-robotics.com:/var/www/abcdk/\n" );
# et aussi dans /www/mangedisque/Alma/NaoStuffs/abcdk :)

time.sleep( 5. );


