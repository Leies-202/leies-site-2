# ���W���[���錾/�ϐ�������
use strict;
my %cf;
#��������������������������������������������������������������������
#�� DAY COUNTER-EX : init.cgi - 2017/05/14
#�� copyright (c) KentWeb, 1997-2017
#�� http://www.kent-web.com/
#��������������������������������������������������������������������
$cf{version} = 'DayX v5.0';
#��������������������������������������������������������������������
#�� [���ӎ���]
#�� 1. ���̃v���O�����̓t���[�\�t�g�ł��B���̃v���O�������g�p����
#��    �����Ȃ鑹�Q�ɑ΂��č�҂͈�؂̐ӔC�𕉂��܂���B
#�� 2. �ݒu�Ɋւ��鎿��̓T�|�[�g�f���ɂ��肢�������܂��B
#��    ���ڃ��[���ɂ�鎿��͈�؂��󂯂������Ă���܂���B
#��������������������������������������������������������������������
#
# [ �^�O�̏������̗� ]
#   ���J�E���g     <img src="count/dayx.cgi?gif" alt="" />
#   �{���̃J�E���g <img src="count/dayx.cgi?today" alt="" />
#   ����@�@�V	   <img src="count/dayx.cgi?yes" alt="" />

#===========================================================
# �� �ݒ荀��
#===========================================================

# �摜�A�����W���[��
# 0 : gifcat.pl
# 1 : Image-Magick�i�T�[�o�ɃC���X�g�[������Ă���K�v����j
$cf{image_pm} = 0;

# �݌v�J�E���g�Œጅ��
$cf{digit1} = 4;

# �{/����J�E���g�Œጅ��
$cf{digit2} = 3;

# �݌v�t�@�C���y�z
$cf{logfile} = "./data/dayx.dat";

# ���/�{���t�@�C���y�T�[�o�p�X�z
$cf{yesfile} = "./data/yes.dat";
$cf{todfile} = "./data/today.dat";

# �����L�^�t�@�C���y�T�[�o�p�X�z
$cf{dayfile} = "./data/day.dat";

# �����L�^�t�@�C���y�T�[�o�p�X�z
$cf{monfile} = "./data/mon.dat";

# �e���v���[�g�f�B���N�g��
$cf{tmpldir} = './tmpl';

# �݌v�J�E���gGIF�摜�f�B���N�g���y�T�[�o�p�X�z
$cf{gifdir1} = "./img/gif1";

# �{/����J�E���gGIF�摜�f�B���N�g���y�T�[�o�p�X�z
$cf{gifdir2} = "./img/gif2";

# �J�E���^�̋@�\�^�C�v
# 0 : ���J�E���g���s�v�i����^�{���̂݁j
# 1 : �W���^�C�v
$cf{type} = 1;

# IP�A�h���X�̓�d�J�E���g�`�F�b�N
# 0 : �`�F�b�N���Ȃ�
# 1 : �`�F�b�N����
$cf{ip_check} = 1;

# �W�v���X�g�^�C�g��
$cf{list_title} = '�W�v���X�g�ꗗ';

# gifcat.pl�̃p�X�y�T�[�o�p�X�z
$cf{gifcat_pl} = './lib/gifcat.pl';

# magick.pl�̃p�X�y�T�[�o�p�X�z
$cf{magick_pl} = './lib/magick.pl';

#===========================================================
# �� �ݒ芮��
#===========================================================

# �ݒ�l��Ԃ�
sub set_init {
	return %cf;
}


1;

