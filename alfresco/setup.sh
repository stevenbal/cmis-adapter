#!/bin/sh

apt-get -y update

#
# Alfresco
#
alfrescoVersion=201707
alfrescoFilename=alfresco-community-installer-$alfrescoVersion-linux-x64.bin
alfrescoDownloadUrl=https://sourceforge.net/projects/alfresco/files/Alfresco%20$alfrescoVersion%20Community/$alfrescoFilename/download

# Install fontconfig dependency for libreoffice
apt-get -y install fontconfig curl libxinerama1 libcups* libglu1-mesa

# Change working dir to vagrant directory
cd /vagrant

# Download Alfresco release if not already downloaded earlier
if [ ! -f $alfrescoFilename ]; then
	echo Downloading Alfresco release: $alfrescoFilename
	curl -L $alfrescoDownloadUrl > $alfrescoFilename
    chmod +x $alfrescoFilename
fi

# Stop Alfresco in case it was installed and running already
service alfresco stop

# Install Alfresco using the key file
./$alfrescoFilename < /vagrant/alfresco-install-keys

# Copy extensions and amp modules
cd /opt/alfresco
#cp -Rv /vagrant/shared-classes/* tomcat/shared/classes/
#cp -Rv /vagrant/shared-lib/* tomcat/shared/lib/
#cp -Rv /vagrant/amps-repo/* amps/
#cp -Rv /vagrant/amps-share/* amps_share/

alfrescoPropertiesFile=/opt/alfresco/tomcat/shared/classes/alfresco-global.properties

if [ ! `grep -q "audit" $alfrescoPropertiesFile` ]; then
    cat <<EOT >> $alfrescoPropertiesFile

audit.enabled=true
audit.alfresco-access.enabled=true
audit.cmischangelog.enabled=true
replication.enabled=false
ftp.enabled=false
nfs.enabled=false
cifs.enabled=false
lucene.indexer.cacheEnabled=false
lucene.indexer.contentIndexingEnabled=false
sync.mode=OFF
syncService.mode=OFF
activities.feed.notifier.enabled=false
activities.feed.max.ageMins=60
ooo.enabled=false
jodconverter.enabled=false
db.schema.update=true
index.recovery.mode=AUTO
system.thumbnail.generate=false
index.subsystem.name=solr4
solr.port.ssl=8443
solr.port=8780
solr.host=localhost
solr.backup.alfresco.remoteBackupLocation=/opt/solr_data/Backups/workspace
solr.backup.archive.remoteBackupLocation=/opt/solr_data/Backups/archive
solr.backup.alfresco.cronExpression=0 0 4 * * ?
solr.backup.archive.cronExpression=0 0 4 * * ?
trashcan-cleaner.cron=0 30 * * * ?
trashcan-cleaner.keepPeriod=P1D
trashcan-cleaner.deleteBatchCount=1000
system.content.eagerOrphanCleanup=true
org.alfresco.integrations.google.docs=false
org.alfresco.integrations.share.google.docs=false
EOT
fi

# Install amp modules into alfresco.war and share.war
mmt="/opt/alfresco/java/bin/java -jar /opt/alfresco/bin/alfresco-mmt.jar"
$mmt install amps tomcat/webapps/alfresco.war -directory $*
$mmt list tomcat/webapps/alfresco.war
$mmt install amps_share tomcat/webapps/share.war -directory $*
$mmt list tomcat/webapps/share.war

# Start Alfresco after installation
service alfresco start
