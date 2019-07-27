#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� DAY COUNTER-EX : dayx.cgi - 2017/05/14
#�� copyright (c) KentWeb, 1997-2017
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;

# �ݒ�t�@�C���捞
require './init.cgi';
my %cf = set_init();

# ����������
my $q = $ENV{QUERY_STRING};
$q =~ s/\W//g;

# ��X�V�n
if ($q eq "yes" || ($cf{type} == 1 && $q eq "today")) {
	
	# �f�[�^�ǂݍ���
	my $count = read_data();
	
	# �摜�\��
	load_image($count);

# �X�V�n
} else {
	
	# �f�[�^�X�V
	my $count = renew_data();
	
	# �摜�\��
	load_image($count);
}

#-----------------------------------------------------------
#  �f�[�^�ǂݍ��݁i��X�V�j
#-----------------------------------------------------------
sub read_data {
	# �����҂i�X�V�n�Ƃ̏Փˉ���j
	select(undef,undef,undef,0.5);
	
	# �L�^�t�@�C���ǂݍ���
	my %data = (today => $cf{todfile}, yes => $cf{yesfile});
	open(DAT,"$data{$q}") or error();
	my $data = <DAT>;
	close(DAT);
	
	return $data;
}

#-----------------------------------------------------------
#  �f�[�^�X�V
#-----------------------------------------------------------
sub renew_data {
	# �L�^�t�@�C���ǂݍ���
	open(DAT,"+< $cf{logfile}") or error();
	eval "flock(DAT,2);";
	my $data = <DAT>;
	
	# �L�^�t�@�C������ [ ��, �݌v, �j��, IP ]
	my ($key,$count,$youbi,$ip) = split(/<>/,$data);
	
	# �����擾
	$ENV{TZ} = "JST-9";
	my ($mday,$mon,$year,$wday) = (localtime(time))[3..6];
	$year += 1900;
	$mon = sprintf("%02d",$mon+1);
	my @week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $thisday = $week[$wday];
	my $date = "$year/$mon";
	
	# IP�`�F�b�N
	my ($flg,$addr);
	if ($cf{ip_check}) {
		$addr = $ENV{REMOTE_ADDR};
		if ($addr eq $ip) { $flg = 1; }
	}
	
	# �J�E���g�A�b�v
	if (!$flg) {
		$count++;
		
		# --- ��������
		if ($key eq $mday) {
			
			# �{���J�E���g�A�b�v
			open(TOD,"+< $cf{todfile}") or error();
			eval "flock(TOD,2);";
			my $today = <TOD> + 1;
			seek(TOD,0,0);
			print TOD $today;
			truncate(TOD,tell(TOD));
			close(TOD);
			
			# �݌v���O�t�H�[�}�b�g
			$data = "$key<>$count<>$thisday<>$addr";
		
		# --- ��������
		} else {
			
			# �{���N���A
			open(TOD,"+< $cf{todfile}") or error();
			eval "flock(TOD,2);";
			my $today = <TOD>;
			seek(TOD,0,0);
			print TOD "1";
			truncate(TOD,tell(TOD));
			close(TOD);
			
			# ����X�V
			open(YES,"+> $cf{yesfile}") or error();
			eval "flock(YES, 2);";
			print YES $today;
			close(YES);
			
			# ���O�t�H�[�}�b�g
			$data = "$mday<>$count<>$thisday<>$addr";
			
			day_count($mday,$key,$mon,$youbi,$today);
			mon_count($date,$today);
		}
		
		# ���O�X�V
		seek(DAT,0,0);
		print DAT $data;
		truncate(DAT,tell(DAT));
	}
	close(DAT);
	
	return $count;
}

#-----------------------------------------------------------
#  �����J�E���g
#-----------------------------------------------------------
sub day_count {
	my ($mday,$key,$mon,$youbi,$today) = @_;
	
	# ���O�̓����L�[���{���̓�����������Ό����ς�����Ɣ��f����
	if ($mday < $key) {
		open(DB,"+> $cf{dayfile}") or error();
		close(DB);
	
	# �����ł̏���
	} else {
		if ($key < 10) { $key = "0$key"; }
		
		open(DB,">> $cf{dayfile}") or error();
		eval "flock(DB,2);";
		print DB "$mon/$key ($youbi)<>$today<>\n";
		close(DB);
	}
}

#-----------------------------------------------------------
#  �����J�E���g
#-----------------------------------------------------------
sub mon_count {
	my ($date,$today) = @_;
	my @mons;
	
	open(MON,"+< $cf{monfile}") or error();
	eval "flock(MON, 2);";
	
	# ���߂ẴA�N�Z�X�̏ꍇ
	if (-z $cf{monfile}) {
		$mons[0] = "$date<>$today<>\n";
	
	# �Q��ڈȍ~
	} else {
		@mons = <MON>;
		
		# ���O�z��̍ŏI�s�𕪉�
		$mons[$#mons] =~ s/\n//;
		my ($y_m,$cnt) = split(/<>/,$mons[$#mons]);
		
		# ��������
		if ($y_m eq $date) {
			$cnt += $today;
			$mons[$#mons] = "$y_m<>$cnt<>\n";
		
		# ��������
		#�i���O�z��̍ŏI�s�� $date�ƈقȂ�΁A�����ς����Ɣ��f����j
		} else {
			$cnt += $today;
			$mons[$#mons] = "$y_m<>$cnt<>\n";
			push(@mons,"$date<>0<>\n");
		}
	}
	
	# ���O�t�@�C���X�V
	seek(MON, 0, 0);
	print MON @mons;
	truncate(MON,tell(MON));
	close(MON);
}

#-----------------------------------------------------------
#  �J�E���^�摜�\��
#-----------------------------------------------------------
sub load_image {
	my ($data) = @_;
	
	my ($digit,$dir);
	if ($q eq 'gif') {
		$digit = $cf{digit1};
		$dir = $cf{gifdir1};
	} else {
		$digit = $cf{digit2};
		$dir = $cf{gifdir2};
	}
	
	# ��������
	while (length($data) < $digit) {
		$data = '0' . $data;
	}
	
	# Image::Magick�̂Ƃ�
	if ($cf{image_pm} == 1) {
		require $cf{magick_pl};
		magick($data, $dir);
	}
	
	# �摜�ǂݍ���
	my @img;
	foreach ( split(//,$data) ) {
		push(@img,"$dir/$_.gif");
	}
	
	# �摜�A��
	require $cf{gifcat_pl};
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);
	print gifcat::gifcat(@img);
}

#-----------------------------------------------------------
#  �G���[����
#-----------------------------------------------------------
sub error {
	# �G���[�摜
	my @err = qw{
		47 49 46 38 39 61 2d 00 0f 00 80 00 00 00 00 00 ff ff ff 2c
		00 00 00 00 2d 00 0f 00 00 02 49 8c 8f a9 cb ed 0f a3 9c 34
		81 7b 03 ce 7a 23 7c 6c 00 c4 19 5c 76 8e dd ca 96 8c 9b b6
		63 89 aa ee 22 ca 3a 3d db 6a 03 f3 74 40 ac 55 ee 11 dc f9
		42 bd 22 f0 a7 34 2d 63 4e 9c 87 c7 93 fe b2 95 ae f7 0b 0e
		8b c7 de 02	00 3b
	};
	
	print "Content-type: image/gif\n\n";
	for (@err) { print pack('C*', hex($_));	}
	exit;
}

