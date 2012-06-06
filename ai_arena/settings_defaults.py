# Django settings for ai_arena project.
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
def ABS_DIR(rel):
  return os.path.join(BASE_DIR, rel.replace('/',os.path.sep))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ai_arena',                      # Or path to database file if using sqlite3.
        'USER': 'ai_arena',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ABS_DIR('media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ABS_DIR('static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2g)b1fya=od#t@j!gnvy^amypd(%7)vek5q+ko93c@9vuv4vh3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'ai_arena.urls'

TEMPLATE_DIRS = (
    ABS_DIR("templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'ai_arena.contests',
    'ai_arena.nadzorca',
    'ai_arena.registration2',
    'captcha',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

RECAPTCHA_PUBLIC_KEY = '6LcqQtESAAAAALMiHq85_8QIaOwevpTe01PoZ4eu'
RECAPTCHA_PRIVATE_KEY = '6LcqQtESAAAAACkn_VW7df3bmEatgsHx4rAldJAO'

AUTH_PROFILE_MODULE = 'contests.UserProfile'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

"Constants section"

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True
DEFAULT_FROM_EMAIL = 'aiarena@aiarena.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='localhost'
EMAIL_PORT='1025'

LANGUAGES = (
    ('C', 'C'),
    ('CPP', 'C++'),
    ('PYTHON', 'Python'),
)

MAKEFILE_DIR = ABS_DIR('../makefile/')
MAKEFILE_PATH = MAKEFILE_DIR + 'Makefile'

# contests/models.py

NAME_LENGTH = 255
LANG_LENGTH = 10
GAME_MIN_PLAYERS_DEFAULT = 1
GAME_MAX_PLAYERS_DEFAULT = 6
COMPILATION_TEMP_DIR = 'compilation_temp'
RULES_DIR = 'game_rules'
JUDGES_BINARIES_DIR = 'game_judges_binaries'
JUDGES_SOURCES_DIR = 'game_judges_sources'
BOTS_BINARIES_DIR = 'game_bots_binaries'
BOTS_SOURCES_DIR = 'game_bots_sources'
CONTEST_REGULATIONS_DIR = 'contests_regulations'
PHOTOS_DIR = 'profiles/photos'

SCORE_DIGITS = 15 
SCORE_DECIMAL_PLACES = 6

# in MB
DEFAULT_GAME_MEMORY_LIMIT = 32
# in miliseconds
DEFAULT_GAME_TIME_LIMIT = 5000

DEFAULT_CONTEST_MEMORY_LIMIT = DEFAULT_GAME_MEMORY_LIMIT
DEFAULT_CONTEST_TIME_LIMIT = DEFAULT_GAME_TIME_LIMIT

# /contests/game_views.py

GAME_RULES_PATH = MEDIA_ROOT + RULES_DIR + '/'
GAME_JUDGE_SOURCES_PATH = MEDIA_ROOT + JUDGES_SOURCES_DIR + '/'
GAME_JUDGE_BINARIES_PATH = MEDIA_ROOT + JUDGES_BINARIES_DIR + '/'
COMPILATION_TEMP_PATH = MEDIA_ROOT + COMPILATION_TEMP_DIR + '/'

# bot create page

BOT_CREATE_FIELD_COLUMNS = 200
BOT_CREATE_FIELD_ROWS = 20 

C_LANGUAGE = 'C'
C_KEYWORDS = ['auto', 'break', 'case', 'const', 'continue', 'default', 'do', 'else', 'enum', 
        'extern', 'for', 'goto', 'if', 'register', 'return', 'signed', 'sizeof', 
        'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'volatile', 'while']
C_TYPES = ['char', 'double', 'float', 'int', 'long', 'short', 'void']

CPP_LANGUAGE = 'CPP'
CPP_KEYWORDS = ['and', 'and_eq', 'alignas', 'alignof', 'asm', 'auto', 'bitand', 'bitor', 
        'break', 'case', 'catch', 'class', 'compl', 'const', 'constexpr', 'const_cast', 'continue', 'decltype', 
        'default', 'delete', 'do', 'dynamic_cast', 'else', 'enum', 'explicit', 
        'export', 'extern', 'false', 'for', 'friend', 'goto', 'if', 
        'inline', 'long', 'mutuable', 'namespace', 'new', 'noexcept',
        'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected',
        'public', 'register', 'reinterpret_cast', 'return', 'signed', 'sizeof', 'static',
        'static_assert', 'static_cast', 'struct', 'switch', 'template', 'this', 'thread_local', 
        'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using',
        'virtual', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq', 'override', 'final']
CPP_TYPES = ['bool', 'char', 'char16_t', 'char32_t', 'double', 'float', 'int', 'long', 'short', 'void']

JAVA_LANGUAGE = 'JAVA'
JAVA_KEYWORDS = ['abstract', 'assert', 'break', 'case', 'catch', 'class', 'const', 
        'continue', 'default', 'do', 'else', 'enum', 'extends', 'final', 'finally', 'for', 'goto',
        'if', 'implements', 'import', 'instanceof', 'interface', 'native', 'new', 'package', 'private',
        'protected', 'public', 'return', 'static', 'staticfp', 'super', 'switch', 'synchronized', 'this', 
        'throw', 'throws', 'transient', 'try', 'volatile', 'while']
JAVA_TYPES = ['boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short', 'void']

PYTHON_LANGUAGE = 'PYTHON'
PYTHON_KEYWORDS = ['and', 'as', 'assert', 'break', 'class', 'contiune', 'def', 'del', 'elif', 'else', 
        'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 
        'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield']
PYTHON_TYPES = []

SOURCE_FORMATS = {
        C_LANGUAGE: '.c',
        CPP_LANGUAGE: '.cpp',
        JAVA_LANGUAGE: '.java',
        PYTHON_LANGUAGE: '.py',
}

# contests/game_launcher.py

GEARMAN_HOST = 'localhost:4730'

TEST_USER_NAME = 'test_user'


# May Contest constants

MAY_MODERATOR_NAME = "may_master"
MAY_CONTEST_NAME = "May Contest"
MAY_CONTEST_BEGIN_DATE = '2012-05-12 00:00'
MAY_CONTEST_END_DATE = '2012-05-16 23:59'
MAY_CONTEST_REGULATIONS_PATH = ABS_DIR("../files/may_game/contest_regulations.txt")
# in MB
MAY_CONTEST_MEMORY_LIMIT = 64
# in miliseconds
MAY_CONTEST_TIME_LIMIT = 5000

MAY_CONTEST_GAME_NAME = "POK"
MAY_CONTEST_GAME_JUDGE_LANG = CPP_LANGUAGE 
MAY_CONTEST_GAME_JUDGE_PATH = ABS_DIR("../files/may_game/pok_judge.cpp")
MAY_CONTEST_JUDGE_MANUAL_PATH = ABS_DIR("../files/may_game/pok_judge_manual.txt")
MAY_CONTEST_BOT_PATH = ABS_DIR("../files/may_game/pok_bot.cpp")
MAY_CONTEST_GAME_RULES_PATH = ABS_DIR("../files/may_game/pok_rules.txt")
MAY_CONTEST_PLAYERS_NUMBER = 2

MAY_CONTEST_EXAMPLE_JUDGE_PATH = MEDIA_URL + "may_contest/judge.cpp"
MAY_CONTEST_EXAMPLE_BOT_PATH = MEDIA_URL + "may_contest/bot.cpp"
MAY_CONTEST_JUDGE_MANUAL_PATH = MEDIA_URL + "may_contest/README.txt"

MAY_CONTEST_DEFAULT_BOT_PATH = ABS_DIR("../files/may_game/pok_bot.cpp")
MAY_CONTEST_DEFAULT_BOT_NAME = "POK_default_bot"
MAY_CONTEST_DEFAULT_BOT_LANG = CPP_LANGUAGE 

MAY_CONTEST_PICNIC_USERNAME = "picnic_user"

PICNIC_DEFAULT_LANGUAGE = PYTHON_LANGUAGE
PICNIC_BOTS_PATH = ABS_DIR("media/picnic_bots/")
PICNIC_DEFAULT_BOTS_NAMES = {
        'bot_code1' : 'Bot Template',
        'bot_code2' : 'Weak Bot',
        'bot_code3' : 'Medium Bot',
        'bot_code4' : 'Strong Bot',
        }

PICNIC_BOT_CODES_FILES = {
        'bot_code1' : ABS_DIR("../files/may_game/default_bots/template_bot.py"),
        'bot_code2' : ABS_DIR("../files/may_game/default_bots/weak_bot.py"),
        'bot_code3' : ABS_DIR("../files/may_game/default_bots/medium_bot.py"),
        'bot_code4' : ABS_DIR("../files/may_game/default_bots/strong_bot.py"),
        }

TEST_BOT_PREFIX = "test_from_"
OPPONENT_TEST_BOT_PREFIX = "opponent_from_"
MAX_BOTS_PER_USER = 10

# Running programs from nadzorca
C_RUN_COMMAND = ""
CPP_RUN_COMMAND = ""
JAVA_RUN_COMMAND = "java "
PYTHON_RUN_COMMAND = "python "
