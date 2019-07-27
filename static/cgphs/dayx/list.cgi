#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� DAY COUNTER-EX : list.cgi - 2017/05/14
#�� copyright (c) KentWeb, 1997-2017
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�t�@�C���捞
require './init.cgi';
my %cf = set_init();

# ���X�g�ꗗ
list_data();

#-----------------------------------------------------------
#  ���X�g�ꗗ
#-----------------------------------------------------------
sub list_data {
	# �݌v�t�@�C���ǂݍ���
	open(IN,"$cf{logfile}") or die "open err: $!";
	my $data = <IN>;
	close(IN);
	
	my ($day) = (split(/<>/,$data))[0];
	
	# �{���t�@�C���ǂݍ���
	open(IN,"$cf{todfile}") or die "open err: $!";
	my $tod = <IN>;
	close(IN);
	
	# ���Ԏ擾
	$ENV{TZ} = "JST-9";
	my ($mday,$mon,$year,$wday) = (localtime(time))[3..6];
	my @week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $date = sprintf("%02d/%02d (%s) ", $mon+1,$mday,$week[$wday]);
	my $this_mon  = sprintf("%04d/%02d", $year+1900,$mon+1);
	
	# �����t�@�C���ǂݍ���
	my ($max,@day);
	open(IN,"$cf{dayfile}") or die "open err: $!";
	while(<IN>) {
		my (undef,$cnt) = split(/<>/);
		
		if ($max < $cnt) { $max = $cnt; }
		push(@day,$_);
	}
	close(IN);
	
	if ($max < $tod) { $max = $tod; }
	push(@day,"$date<>$tod<>\n");
	
	# �O���t���̌W���i�ō��l��240px�j
	my $key = 240 / $max;
	
	# �����t�@�C����ǂݍ���
	my ($max2,@mon);
	open(IN,"$cf{monfile}") or die "open err: $!";
	while(<IN>) {
		my (undef,$cnt) = split(/<>/);
		
		if ($max2 < $cnt) { $max2 = $cnt; }
		push(@mon,$_);
	}
	close(IN);
	
	# �O���t���̌W���i�ō��l��240px�j
	
	open(IN,"$cf{tmpldir}/day-graph.txt");
	my $day_graph = join('', <IN>);
	close(IN);
	
	open(IN,"$cf{tmpldir}/day-item.txt");
	my $day_date = join('', <IN>);
	close(IN);
	
	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/list.html") or die "open err: $!";
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!list_title!/$cf{list_title}/g;
	$tmpl =~ s/!this_month!/$this_mon/g;
	
	# ����
	my ($chart_day,$graph,$date,$last_day);
	my $i = 0;
	for (@day) {
		chomp;
		my ($md,$dcnt) = split(/<>/);
		
		# �O���t�����w��
		my $width;
		if ($dcnt > 0) {
			$width = int($dcnt * $key);
		} else {
			$width = 1;
		}
		if ($width < 1) { $width = 1; }
		
		# ������
		$dcnt = comma($dcnt);
		
		$md =~ m|\d+/(\d+) \((..).\)|;
		my $day = $last_day = $1;
		my $week = $2;
		$day =~ s/^0//;
		$day =
			$week eq 'Sa' ? qq|<span style="color:blue">$day<br />$week</span>| :
			$week eq 'Su' ? qq|<span style="color:red">$day<br />$week</span>| :
				qq|$day<br />$week|;
		
		# ���[�v
		my $tmp1 = $day_graph;
		$tmp1 =~ s/!count!/$dcnt/g;
		$tmp1 =~ s/!height!/$width/g;
		$graph .= $tmp1;
		
		my $tmp2 = $day_date;
		$tmp2 =~ s|!date!|$day|g;
		$date .= $tmp2;
	}
	
	$tmpl =~ s/<!-- day:graph -->/$graph/;
	$tmpl =~ s/<!-- day:date -->/$date/;
	
	# �e���v���[�g����
	my ($head,$loop,$foot) = split(/<!-- loop -->/s,$tmpl);
	
	# �\���J�n
	print "Content-type: text/html; charset=shit_jis\n\n";
	print $head;
	
	# ����
	for (@mon) {
		my ($ym,$mcnt) = split(/<>/);
		my ($year,$mon) = split(/\//,$ym);
		
		my $avr;
		
		# �����F����͓����f�[�^�̐�
		if ($_ eq $mon[$#mon]) {
			if ($mcnt > 0) {
				$avr = int (($mcnt / $last_day) + 0.5);
				$avr = comma($avr);
			} else {
				$avr = ' - ';
			}
			
		# �����ȊO�F���ꂪ���̌��̖���
		} else {
			my $last = last_day($year,$mon);
			$avr = int (($mcnt / $last) + 0.5);
			$avr = comma($avr);
		}
		
		# �O���t�����w��
		my $width;
		if ($mcnt > 0) {
		} else {
			$width = 1;
		}
		if ($width < 1) { $width = 1; }
		
		# ������
		$mcnt = comma($mcnt);
		
		# ���[�v
		my $tmp = $loop;
		$tmp =~ s/!date!/$ym/g;
		$tmp =~ s/!month!/$mcnt/g;
		$tmp =~ s/!average!/$avr/g;
		$tmp =~ s/!width!/$width/g;
		print $tmp;
	}
	
	# �t�b�^
	footer($foot);
}

#-----------------------------------------------------------
#  ���̖���
#-----------------------------------------------------------
sub last_day {
	my ($year,$mon) = @_;
	
	my $last = (31,28,31,30,31,30,31,31,30,31,30,31)[$mon - 1]
	+ ($mon == 2 && (($year % 4 == 0 && $year % 100 != 0) || $year % 400 == 0));
	
	return $last;
}

#-----------------------------------------------------------
#  ���悫��
#-----------------------------------------------------------
sub comma {
	local($_) = @_;
	
	1 while s/(.*\d)(\d\d\d)/$1,$2/;
	$_;
}

#-----------------------------------------------------------
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;
	
	# ���쌠�\�L�i�폜�֎~�j
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="http://www.kent-web.com/" target="_top">DayCounterEX</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

