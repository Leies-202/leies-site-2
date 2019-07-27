# ���W���[���錾/�ϐ�������
use strict;
my %cf;
#��������������������������������������������������������������������
#�� �A�N�Z�X��̓V�X�e��
#�� Access Report : init.cgi - 2013/03/24
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������
$cf{version} = 'Access Report v5.5';
#��������������������������������������������������������������������
#�� [���ӎ���]
#�� 1. ���̃X�N���v�g�̓t���[�\�t�g�ł��B���̃X�N���v�g���g�p����
#��    �����Ȃ鑹�Q�ɑ΂��č�҂͈�؂̐ӔC�𕉂��܂���B
#�� 2. �ݒu�Ɋւ��鎿��̓T�|�[�g�f���ɂ��肢�������܂��B
#��    ���ڃ��[���ɂ�鎿��͈�؂��󂯂������Ă���܂���B
#��������������������������������������������������������������������
#
# [ (1) CGI���[�h : �^�O�̓\��t������ ]
#  ���ȉ��̃^�O���A�K�� <body>�`</body> �ԂɋL�q���ĉ�����
# <script type="text/javascript">
# <!--
# document.write("<img src='http://www.example.com/report.cgi?");
# document.write(escape(document.referrer)+"' width='1' height='1'>");
# // -->
# </script>
# <noscript>
# <img src="http://www.example.com/report.cgi" width="1" height="1">
# </noscript>
#
# [ (2) SSI���[�h : �^�O�̓\��t������ ]
#
# <!--#exec cgi="./cgi-bin/report.cgi"-->

#===========================================================
# �� ��{�ݒ�
#===========================================================

# �{����ʂ̓����p�X���[�h
# �� �p�X���[�h���󗓂ɂ���Ɠ�����ʂȂ��ŉ{���\
$cf{pass} = 'trrm5492';

# SSI���[�h (0=no 1=yes)
# �� SSI�̗��p�\�ȃT�[�o����i�Ăяo���^�O�ɒ��Ӂj
$cf{ssi} = 0;

# ���O�t�@�C���y�T�[�o�p�X�z
$cf{logfile} = './data/log.cgi';

# �e���v���[�g�f�B���N�g��
$cf{tmpldir} = './tmpl';

# �ő働�O�ێ����i����ȏ�傫�����Ȃ���������j
$cf{maxlog} = 1000;

# �A�g�����_���@�\
# �� 0�ȊO�ŗL���B���̐��l�̊m���ł������O�ۑ����s��Ȃ��B
# �� 1������̖K��񐔂���L$cf{maxlog}��𒴂���T�C�g�̏ꍇ�A���ԑт̕��������s���@�\�B
# �� ��F$cf{rand} = 100; �ł���΁A�m���I��100���1�x�����W�v���s��Ȃ��B
$cf{rand} = 0;

# �����N�����O�y�[�W�i���p�X�y�[�X�ŋ�؂�j
# �� �����Ŏw�肵��URL�́u�����N���v�W�v���珜�O����܂�
# �� ��F$cf{myurl} = 'http://www.example.com/ http://www.example.jp/';
$cf{myurl} = 'http://eizi2002.skr.jp/';

# �z�X�g/IP�A�h���X�ɂ�鏜�O�i���p�X�y�[�X�ŋ�؂�j
# �� �����Ŏw�肵��URL�́u�����N���v�W�v���珜�O����܂�
# �� ��F$cf{deny_host} = '.anonymizer.com 225.12.23.';
$cf{deny_host} = '.tokai.or.jp';

# IP�A�h���X�`�F�b�N�ɂ���d�L�^�r�� (0=no 1=yes)
$cf{ip_chk} = 0;

## --- < ������艺�͈ꗗ���X�g�̐ݒ� > --- ##

# ���X�g�t�@�C���yURL�p�X�z
$cf{list_cgi} = './list.cgi';

# �z�[���y�[�W�^�C�g��
$cf{list_title} = "My HomePage";

# ���X�g�ꗗ����̖߂�� (��΃p�X�Ȃ� http://�����URL�ŋL�q�j
$cf{homepage} = "/index.html";

# �O���t�摜�i��΃p�X�Ȃ� http://�����URL�ŋL�q�j
$cf{graph1} = "./img/graph1.gif";  # ����
$cf{graph2} = "./img/graph2.gif";  # �c��

# ���X�g�Œ�\�������i����ɖ����Ȃ����͔�\���j
$cf{max_ref} = 2;	# �����N��
$cf{max_os}  = 2;	# OS���
$cf{max_ag}  = 2;	# �u���E�U
$cf{max_hos} = 5;	# �z�X�g��

#===========================================================
# �� �ݒ芮��
#===========================================================

# �ݒ�l��Ԃ�
sub init {
	return %cf;
}



1;

