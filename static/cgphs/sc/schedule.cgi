#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Web Scheduler : init.cgi - 2015/04/26
#│ copyright (c) KentWeb, 1997-2015
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;

# 設定ファイル認識
require "./init.cgi";
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
error('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# 主要処理
if ($in{form}) { form_date(); }
if ($in{mode} eq 'put_log') { put_log(); }
list_calen();

#-----------------------------------------------------------
#  リスト表示
#-----------------------------------------------------------
sub list_calen {
	# 年月引数解釈
	if ($in{date} =~ m|^(\d{4})/(\d{2})|) {
		$in{y} = $1;
		$in{m} = $2;
	} elsif ($in{y} && $in{m}) {
		$in{y} =~ s/\D//g;
		$in{m} =~ s/\D//g;
	}
	
	# 本日
	my ($mday,$mon,$year) = (localtime())[3..5];
	$year += 1900;
	$mon  = sprintf("%02d",$mon + 1);
	$mday = sprintf("%02d",$mday);
	my $today;
	if ($in{y} !~ /^\d{4}$/ || $in{m} > 12 || $in{m} < 1) {
		$in{y} = $year;
		$in{m} = $mon;
		$today = $mday;
	} elsif ($in{y} == $year && $in{m} == $mon) {
		$today = $mday;
	}
	
	# 前月/翌月ボタン
	my ($btn_back,$btn_next);
	if ($in{m} == 1) {
		my $y = sprintf("%04d",$in{y}-1);
		$btn_back = "y=$y&amp;m=12";
		$btn_next = "y=$in{y}&amp;m=02";
	} elsif ($in{m} == 12) {
		my $y = sprintf("%04d",$in{y}+1);
		$btn_back = "y=$in{y}&amp;m=11";
		$btn_next = "y=$y&amp;m=01";
	} else {
		my $mb = sprintf("%02d",$in{m}-1);
		my $mn = sprintf("%02d",$in{m}+1);
		$btn_back = "y=$in{y}&amp;m=$mb";
		$btn_next = "y=$in{y}&amp;m=$mn";
	}
	
	# 末日
	require './lib/holiday.pl';
	my $last = holiday::last_day($in{y},$in{m});
	
	# 初日の曜日
	my $week = holiday::get_week($in{y},$in{m},1);
	
	# 年月データ認識
	my $log = sprintf("%04d%02d",$in{y},$in{m});
	my (%tim,%act);
	open(IN,"$cf{logdir}/$log.dat");
	while(<IN>) {
		chomp;
		my ($no,$day,$fr1,$fr2,$to1,$to2,$act,$ex) = split(/<>/);
		
		# 時間
		my $time = $to1 eq '' ? "$fr1:$fr2～" : "$fr1:$fr2～$to1:$to2";
		$tim{$day} .= "<br />\n" if (defined($tim{$day}));
		$tim{$day} .= $time;
		
		# 内容
		$act{$day} .= "<br />\n" if (defined($act{$day}));
		$act .= qq|<a href="$cf{uplurl}/$no.$ex" target="_blank"><img src="$cf{cmnurl}/$cf{icon}{$ex}" alt="$ex" class="ico" /></a>| if ($ex);
		$act{$day} .= $act;
	}
	close(IN);
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/list.html") or error('open err: list.html');
	my $tmpl = join('', <IN>);
	close(IN);
	
	# 文字置換え
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!title!/$cf{title}/g;
	$tmpl =~ s/!year!/$in{y}/g;
	$tmpl =~ s/!mon!/$in{m}/g;
	$tmpl =~ s/!(\w+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	$tmpl =~ s|!btn-back!|<a href="$cf{index_cgi}?$btn_back"><img src="$cf{cmnurl}/back.png" alt="前月" class="icon" /></a>|g;
	$tmpl =~ s|!btn-next!|<a href="$cf{index_cgi}?$btn_next"><img src="$cf{cmnurl}/next.png" alt="翌月" class="icon" /></a>|g;
	$tmpl =~ s|!btn-this!|<a href="$cf{index_cgi}"><img src="$cf{cmnurl}/now.png" alt="当月" /></a>|g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="" class="icon" />|g;
	
	# テンプレート分割
	my ($head,$loop,$foot) = split(/<!-- loop -->/s,$tmpl);
	
	# 祝日定義
	my %hol = holiday::holi_mon($in{y},$in{m});
	
	# ヘッダー表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 内容表示
	my $w = $week;
	foreach my $i (1 .. $last) {
		
		# 日を２桁化
		my $d = sprintf("%02d",$i);
		
		# 祝日チェック
		my $css_week;
		if (defined($hol{$d})) {
			$css_week = "color:$cf{wkcol}[7];";
			$act{$i} = qq|<span style="$css_week;font-size:smaller">$hol{$d}</span><br />$act{$i}|;
			$tim{$i} = "&nbsp;<br />$tim{$i}";
		} else {
			$css_week = "color:$cf{wkcol}[$w];";
		}
		
		# 本日
		my $css_back = "text-align:left;";
		if ($today == $i) {
			$css_back .= "background:$cf{wkcol}[8];";
			$css_week .= "background:$cf{wkcol}[8];";
		}
		
		# 文字置換え
		my $tmp = $loop;
		$tmp =~ s/!css-week!/$css_week/g;
		$tmp =~ s/!css-back!/$css_back/g;
		$tmp =~ s|!day!|<a href="$cf{index_cgi}?form=$in{y}$in{m}$d" style="$css_week">$i</a>|g;
		$tmp =~ s/!week!/$cf{week}->[$w]/g;
		$tmp =~ s/!time!/$tim{$i}/g;
		$tmp =~ s/!action!/$act{$i}/g;
		print $tmp;
		
		# 曜日フラグ
		$w = $w == 6 ? 0 : ++$w;
	}
	
	# フッター表示
	footer($foot);
}

#-----------------------------------------------------------
#  書き込みフォーム
#-----------------------------------------------------------
sub form_date {
	# 引数チェック
	my ($y,$m,$d) = $in{form} =~ /^(\d{4})(\d{2})(\d{2})$/
			? ($1,$2,$3)
			: error('不正な要求です');
	
	# 該当データ抽出
	my @log;
	open(IN,"$cf{logdir}/$y$m.dat");
	while(<IN>) {
		chomp;
		my ($no,$day,$fr1,$fr2,$to1,$to2,$act,$ex) = split(/<>/);
		
		if ($day == $d) { push(@log,$_); }
	}
	close(IN);
	
	# 曜日
	require './lib/holiday.pl';
	my $week = holiday::get_week($y,$m,$d);
	my $date = "$y年$m月$d日（$cf{week}->[$week]）";
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/form.html") or error('open err: form.html');
	my $tmpl = join('', <IN>);
	close(IN);
	
	# 文字置換え
	$tmpl =~ s/!title!/$cf{title}/g;
	$tmpl =~ s/!(\w+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!date!/$date/g;
	$tmpl =~ s/!y!/$y/g;
	$tmpl =~ s/!m!/$m/g;
	$tmpl =~ s/!d!/$d/g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="" class="icon" />|g;
	
	# テンプレート分割
	my ($head,$loop,$foot) = split(/<!-- loop -->/s,$tmpl);
	
	# 新規フォーム
	$head =~ s/<!-- op_from_h -->/op_h()/eg;
	$head =~ s/<!-- op_from_m -->/op_m()/eg;
	$head =~ s/<!-- op_to_h -->/op_h()/eg;
	$head =~ s/<!-- op_to_m -->/op_m()/eg;
	
	# ヘッダー表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# メンテ用フォーム
	my $i = 0;
	foreach (@log) {
		$i++;
		my ($no,$day,$fr1,$fr2,$to1,$to2,$act,$ex) = split(/<>/);
		
		# 添付有り
		my $upf;
		if ($ex) {
			$upf .= qq|&nbsp; [<a href="$cf{uplurl}/$no.$ex" target="_blank">添付</a>]\n|;
			$upf .= qq|<input type="checkbox" name="del" value="1" />削除\n|;
		}
		
		my $tmp = $loop;
		$tmp =~ s/form-ttl-new/form-ttl-edit/g;
		$tmp =~ s/!form-num!/$i/g;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!action!/$act/g;
		$tmp =~ s/<!-- op_from_h -->/op_h($fr1)/eg;
		$tmp =~ s/<!-- op_from_m -->/op_m($fr2)/eg;
		$tmp =~ s/<!-- op_to_h -->/op_h($to1)/eg;
		$tmp =~ s/<!-- op_to_m -->/op_m($to2)/eg;
		$tmp =~ s/<!-- upfile -->/$upf/;
		print $tmp;
	}
	
	# フッター表示
	footer($foot);
}

#-----------------------------------------------------------
#  プルダウン：時間
#-----------------------------------------------------------
sub op_h {
	my $h = shift;

	my $ret;
	for my $i ( 0 .. 23 ) {
		$i = sprintf("%02d",$i);

		if ($h eq $i) {
			$ret .= qq|<option value="$i" selected="selected">$i</option>\n|;
		} else {
			$ret .= qq|<option value="$i">$i</option>\n|;
		}
	}
	$ret;
}

#-----------------------------------------------------------
#  プルダウン：分
#-----------------------------------------------------------
sub op_m {
	my $m = shift;

	my $ret;
	for ( my $i = 0; $i <= 55; $i += 5 ) {
		$i = sprintf("%02d",$i);

		if ($m eq $i) {
			$ret .= qq|<option value="$i" selected="selected">$i</option>\n|;
		} else {
			$ret .= qq|<option value="$i">$i</option>\n|;
		}
	}
	$ret;
}

#-----------------------------------------------------------
#  ログ更新
#-----------------------------------------------------------
sub put_log {
	# パスワード認証
	error('パスワードが認証できません') if ($in{pwd} ne $cf{password});
	
	# 入力チェック
	if ($in{y} !~ /^\d{4}$/ || $in{m} > 12 || $in{m} < 1) {
		error('不正な要求です');
	}
	my $err;
	if ($in{from_h} eq '' || $in{from_m} eq '') { $err .= "開始時間が未選択です<br />"; }
	if ($in{action} eq '') { $err .= "内容が未入力です<br />"; }
	error($err) if ($err);
	
	# ログ用の「日」
	my $d = $in{d};
	$d =~ s/^0//;
	
	# 新規の場合：採番
	my $new;
	if ($in{num} eq 'new') {
		open(DAT,"+< $cf{numfile}") or error("open err: $cf{numfile}");
		$new = <DAT> + 1;
		seek(DAT, 0, 0);
		print DAT $new;
		truncate(DAT, tell(DAT));
		close(DAT);
	}
	
	# アップロード
	my $upno = $new ? $new : $in{num};
	my $ext = upload_file($upno) if ($in{upfile});
	
	# 当月データがない場合
	if (! -f "$cf{logdir}/$in{y}$in{m}.dat") {
		open(DAT,"+> $cf{logdir}/$in{y}$in{m}.dat") or error("write err: $in{y}$in{m}.dat");
		close(DAT);
		chmod(0666,"$cf{logdir}/$in{y}$in{m}.dat");
	}
	# 書き込みオープン
	my (@tmp1,@tmp2,@log);
	open(DAT,"+< $cf{logdir}/$in{y}$in{m}.dat");
	while(<DAT>) {
		chomp;
		my ($no,$day,$fr1,$fr2,$to1,$to2,$act,$ex) = split(/<>/);
		
		# 編集のとき
		if ($in{job_edit} && $in{num} == $no) {
			
			# 添付削除
			if ($ex && $in{del}) {
				unlink("$cf{upldir}/$no.$ex");
				$ex = '';
			}
			
			# 添付有り
			if ($ext) {
				unlink("$cf{upldir}/$no.$ex") if ($ex && $ex ne $ext);
				$ex = $ext;
			}
			$_ = "$no<>$d<>$in{from_h}<>$in{from_m}<>$in{to_h}<>$in{to_m}<>$in{action}<>$ex<>";
			$day = $d;
			$fr1 = $in{from_h};
			$fr2 = $in{from_m};
			
		# 削除のとき
		} elsif ($in{job_dele} && $in{num} == $no) {
			next;
		}
		
		push(@tmp1,$day);
		push(@tmp2,"$fr1$fr2");
		push(@log,"$_\n");
	}
	
	# 新規の場合
	if ($in{num} eq 'new') {
		push(@tmp1,$in{d});
		push(@tmp2,"$in{from_h}$in{from_m}");
		push(@log,"$new<>$d<>$in{from_h}<>$in{from_m}<>$in{to_h}<>$in{to_m}<>$in{action}<>$ext<>\n");
	}
	
	# 日時順にソートする
	@log = @log[sort{$tmp1[$a] <=> $tmp1[$b] || $tmp2[$a] <=> $tmp2[$b]} 0 .. $#tmp1];
	
	# データ更新
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my $cgi = shift;
	
	my %in;
	foreach ( $cgi->param() ) {
		my $val = $cgi->param($_);
		
		if ($_ ne 'upfile') {
			# 無効化
			$val =~ s/&/&amp;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/'/&#39;/g;
			$val =~ s/[\r\n]//g;
		}
		$in{$_} = $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="http://www.kent-web.com/" target="_top">WebScheduler</a> -
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

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub error {
	my $err = shift;
	
	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!error!/$err/g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  添付アップロード
#-----------------------------------------------------------
sub upload_file {
	my $no = shift;
	
	# 拡張子取得
	my $ext = $cgi->param_filename('upfile') =~ /\.(docx?|xlsx?|pptx?|pdf|zip)$/i
			? $1
			: error("拡張子不明");
	$ext =~ tr/A-Z/a-z/;
	
	# 添付ファイル定義
	my $upfile = "$cf{upldir}/$no.$ext";
	
	# アップロード
	open(UP,"+> $upfile") or error("up err: $upfile");
	binmode(UP);
	print UP $in{upfile};
	close(UP);
	
	# パーミッションを666へ
	chmod(0666,$upfile);
	
	# 結果を返す
	return $ext;
}

