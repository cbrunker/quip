import re
from collections import namedtuple
from os import path

####################
# Global references
####################
# Reference object for friend
Friend = namedtuple('Friend', ['uid', 'mask', 'alias', 'avatar', 'comment', 'status'])

# Emoticon reference
EMOTICONS = {':angel:': ':/quip/Images/emoticons/angel.png',
            ':angry:': ':/quip/Images/emoticons/angry.png',
            ':beer:': ':/quip/Images/emoticons/beer.png',
            ':bigsmile:': ':/quip/Images/emoticons/bigsmile.png',
            ':blue:': ':/quip/Images/emoticons/blue.png',
            ':blush:': ':/quip/Images/emoticons/blush.png',
            ':broken:': ':/quip/Images/emoticons/broken.png',
            ':cake:': ':/quip/Images/emoticons/cake.png',
            ':clown:': ':/quip/Images/emoticons/clown.png',
            ':cocktail:': ':/quip/Images/emoticons/cocktail.png',
            ':confused:': ':/quip/Images/emoticons/confused.png',
            ':cool:': ':/quip/Images/emoticons/cool.png',
            ':cross:': ':/quip/Images/emoticons/cross.png',
            ':crying:': ':/quip/Images/emoticons/crying.png',
            ':devil:': ':/quip/Images/emoticons/devil.png',
            ':gift:': ':/quip/Images/emoticons/gift.png',
            ':glasses:': ':/quip/Images/emoticons/glasses.png',
            ':grin:': ':/quip/Images/emoticons/grin.png',
            ':heart:': ':/quip/Images/emoticons/heart.png',
            ':hugleft:': ':/quip/Images/emoticons/hugleft.png',
            ':hug:': ':/quip/Images/emoticons/hug.png',
            ':kiss:': ':/quip/Images/emoticons/kiss.png',
            ':laughing:': ':/quip/Images/emoticons/laughing.png',
            ':laugh:': ':/quip/Images/emoticons/laugh.png',
            ':love:': ':/quip/Images/emoticons/love.png',
            ':meh:': ':/quip/Images/emoticons/meh.png',
            ':minus:': ':/quip/Images/emoticons/minus.png',
            ':mmm:': ':/quip/Images/emoticons/mmm.png',
            ':ninja:': ':/quip/Images/emoticons/ninja.png',
            ':pink:': ':/quip/Images/emoticons/pink.png',
            ':pirate:': ':/quip/Images/emoticons/pirate.png',
            ':pizza:': ':/quip/Images/emoticons/pizza.png',
            ':plate:': ':/quip/Images/emoticons/plate.png',
            ':plus:': ':/quip/Images/emoticons/plus.png',
            ':quiet:': ':/quip/Images/emoticons/quiet.png',
            ':rose:': ':/quip/Images/emoticons/rose.png',
            ':sad:': ':/quip/Images/emoticons/sad.png',
            ':sick:': ':/quip/Images/emoticons/sick.png',
            ':sleeping:': ':/quip/Images/emoticons/sleeping.png',
            ':sleep:': ':/quip/Images/emoticons/sleep.png',
            ':smile:': ':/quip/Images/emoticons/smile.png',
            ':smirk:': ':/quip/Images/emoticons/smirk.png',
            ':star:': ':/quip/Images/emoticons/star.png',
            ':tick:': ':/quip/Images/emoticons/tick.png',
            ':tired:': ':/quip/Images/emoticons/tired.png',
            ':tounge:': ':/quip/Images/emoticons/tounge.png',
            ':whoah:': ':/quip/Images/emoticons/whoah.png',
            ':wilted:': ':/quip/Images/emoticons/wilted.png',
            ':wink:': ':/quip/Images/emoticons/wink.png',
            ':woops:': ':/quip/Images/emoticons/woops.png',
            ':worried:': ':/quip/Images/emoticons/worried.png'}

MIMETYPES = {'.a': 'application-octet-stream',
             '.ac3': 'audio-ac3',
            '.ai': 'application-postscript',
            '.aif': 'audio-x-aiff',
            '.aifc': 'audio-x-aiff',
            '.aiff': 'audio-x-aiff',
            '.au': 'audio-x-generic',
            '.avi': 'video-x-generic',
            '.bash': 'application-x-shellscript',
            '.bat': 'text-plain',
            '.bin': 'application-octet-stream',
            '.bmp': 'image-x-generic',
            '.bz': 'application-x-bzip',
            '.bz.tar': 'applicaiton-x-bzip-compressed-tar',
            '.c': 'text-plain',
            '.cpio': 'application-x-cpio',
            '.csh': 'application-x-shellscript',
            '.cs': 'text-csharp',
            '.css': 'text-css',
            '.deb': 'application-x-deb',
            '.dll': 'application-octet-stream',
            '.doc': 'application-msword',
            '.dot': 'application-msword',
            '.eml': 'message-rfc822',
            '.eps': 'application-postscript',
            '.epub': 'application-epub+zip',
            '.exe': 'application-octet-stream',
            '.flac': 'audio-x-flac',
            '.gif': 'image-x-generic',
            '.gnumeric': 'application-x-gnumeric',
            '.gtar': 'application-x-tar',
            '.gz': 'application-x-gzip',
            '.gzip': 'application-x-gzip',
            '.h': 'text-plain',
            '.hex': 'text-x-hex',
            '.htm': 'text-html',
            '.html': 'text-html',
            '.ief': 'image-x-generic',
            '.iso': 'application-x-cd-image',
            '.jar': 'application-x-java',
            '.jpe': 'image-x-generic',
            '.jpeg': 'image-x-generic',
            '.jpg': 'image-x-generic',
            '.js': 'application-x-javascript',
            '.ksh': 'application-x-shellscript',
            '.latex': 'application-x-tex',
            '.lzma': 'application-x-lzma-compressed-tar',
            '.m1v': 'video-x-generic',
            '.m3u': 'audio-x-generic',
            '.m3u8': 'video-x-generic',
            '.man': 'application-x-troff-man',
            '.me': 'application-x-troff-man',
            '.mht': 'message-rfc822',
            '.mhtml': 'message-rfc822',
            '.midi': 'audio-midi',
            '.mobi': 'application-epub+zip',
            '.mov': 'video-quicktime',
            '.movie': 'video-x-sgi-movie',
            '.mp2': 'video-x-generic',
            '.mp3': 'video-x-generic',
            '.mp4': 'video-x-generic',
            '.mpa': 'video-x-generic',
            '.mpe': 'video-x-generic',
            '.mpeg': 'video-x-generic',
            '.mpg': 'video-x-generic',
            '.nws': 'message-rfc822',
            '.nzb': 'application-x-nzb',
            '.o': 'application-octet-stream',
            '.obj': 'application-octet-stream',
            '.ogg': 'audio-x-flac+ogg',
            '.otf': 'application-x-font-otf',
            '.p12': 'application-pgp-encrypted',
            '.p7c': 'application-pgp-encrypted',
            '.pbm': 'image-x-generic',
            '.pem': 'application-pgp-encrypted',
            '.pdf': 'application-pdf',
            '.pfx': 'application-pgp-encrypted',
            '.pgm': 'image-x-generic',
            '.php': 'application-x-php',
            '.pl': 'application-x-perl',
            '.png': 'image-x-generic',
            '.pnm': 'image-x-generic',
            '.pot': 'application-vnd.ms-powerpoint',
            '.ppa': 'application-vnd.ms-powerpoint',
            '.ppm': 'image-x-generic',
            '.pps': 'application-vnd.ms-powerpoint',
            '.ppt': 'application-vnd.ms-powerpoint',
            '.ps': 'application-postscript',
            '.pwz': 'application-vnd.ms-powerpoint',
            '.py': 'text-x-python',
            '.pyc': 'application-x-python-bytecode',
            '.pyo': 'application-octet-stream',
            '.qml': 'text-x-qml',
            '.qt': 'video-x-generic',
            '.ra': 'audio-vn.rn-realmedia',
            '.rar': 'application-x-rar',
            '.ram': 'audio-vnd.rn-realvideo',
            '.ras': 'image-x-generic',
            '.rb': 'application-x-ruby',
            '.rbw': 'application-x-ruby',
            '.rdf': 'application-xml',
            '.rgb': 'image-x-generic',
            '.rpm': 'application-x-rpm',
            '.rtf': 'text-rtf',
            '.rtx': 'text-x-generic',
            '.sgm': 'text-sgml',
            '.sgml': 'text-sgml',
            '.sh': 'application-x-shellscript',
            '.snd': 'audio-x-generic',
            '.so': 'application-octet-stream',
            '.speex': 'audio-x-speex+ogg',
            '.sql': 'text-x-sql',
            '.sqlite': 'text-x-sql',
            '.srt': 'application-x-srt',
            '.svg': 'image-svg+xml',
            '.swf': 'application-x-shockwave-flash',
            '.tar': 'application-x-tar',
            '.tcl': 'text-x-tcl',
            '.tex': 'text-x-tex',
            '.texi': 'text-x-texinfo',
            '.texinfo': 'text-x-texinfo',
            '.tgif': 'application-x-tgif',
            '.tgz': 'application-x-tarz',
            '.tif': 'image-x-generic',
            '.tiff': 'image-x-generic',
            '.torrent': 'application-x-bittorrent',
            '.tsv': 'text-csv',
            '.ttf': 'application-x-font-ttf',
            '.txt': 'text-plain',
            '.vcf': 'text-x-vcard',
            '.wav': 'audio-x-wav',
            '.wiz': 'application-msword',
            '.wsdl': 'application-xml',
            '.xbm': 'image-x-generic',
            '.xhtml': 'application-xhtml+xml.png',
            '.xlb': 'application-vnd.ms-excel',
            '.xls': 'application-vnd.ms-excel',
            '.xml': 'text-xml',
            '.xpdl': 'application-xml',
            '.xpm': 'image-x-generic',
            '.xsl': 'application-xml',
            '.xslt': 'application-xlst+xml',
            '.xwd': 'image-x-generic',
            '.zip': 'application-zip'}

EMOTICON_RESOURCES = {r: t for t, r in EMOTICONS.items()}

# flag image directory relative path
FLAGS = path.join('Resources', 'Images', 'flags')
EXT = path.join('Resources', 'Images', 'extensions')

#################
# Regex patterns
#################
# basic url finding pattern
URL_PATTERN = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
# emoticon format
EMOTE_PATTERN = re.compile(r':\w+:')
# resource pattern format
RESOURCE_PATTERN = re.compile(r'<img src=":/quip/Images/\S+png" />')