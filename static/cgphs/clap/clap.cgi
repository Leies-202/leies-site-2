#!/usr/local/bin/perl

#Web Clap Ver 2.09 (2007/07/02)
#
#Copyright(C) 2002-2007 Knight, All rights reserved.
#Mail ... support@web-liberty.net
#Home ... http://www.web-liberty.net/

#――――― 初期処理 ――――――――――――――――――――――――

package main;

use strict;
use lib qw(./lib);

use webliberty::Basis;
use webliberty::Parser;
use webliberty::String;
use webliberty::File;
use webliberty::Host;
use webliberty::Lock;
use webliberty::Skin;
use webliberty::Sendmail;

require './init.cgi';

#――――― メイン処理 ―――――――――――――――――――――――

my $init = &init::get_init;

my $basis_ins  = new webliberty::Basis;
my $parser_ins = new webliberty::Parser(jcode => $init->{jcode_mode});

my $agent;
if ($ENV{'HTTP_USER_AGENT'} =~ /(DoCoMo|SoftBank|Vodafone|J-PHONE|KDDI-|UP\.Browser|DDIPOCKET|WILLCOM)/i) {
	require Jcode;

	$agent = 'mobile';
}

&regist;
if ($init->{limit_count}) {
	&check_limit;
}
&complete;

exit;

#――――― サブルーチン ――――――――――――――――――――――

### データ登録
sub regist {
	my($message, $page);
	if ($agent eq 'mobile') {
		$message = Jcode->new($parser_ins->get_query('message'), 'sjis')->utf8;
		$page    = Jcode->new($parser_ins->get_query('page'), 'sjis')->utf8;
	} else {
		$message = $parser_ins->get_query('message');
		$page    = $parser_ins->get_query('page');
	}

	my $message_ins = new webliberty::String($message);
	my $count_ins   = new webliberty::String($parser_ins->get_query('count'));
	my $page_ins    = new webliberty::String($page);

	$count_ins->create_number;
	$message_ins->create_text;
	$page_ins->create_line;

	#ホストチェック
	my $host_ins = new webliberty::Host;
	foreach (@{$init->{refuse_host}}) {
		if ($_ and $host_ins->get_host =~ /$_/i) {
			if ($init->{error_mode}) {
				&error($host_ins->get_host . "からの拍手は禁止されています。");
			} else {
				return;
			}
		}
	}

	#登録内容チェック
	if ($message_ins->get_string) {
		if ($message_ins->check_length > $init->{max_message} * 2) {
			if ($init->{error_mode}) {
				&error("メッセージの長さは全角$init->{max_message}文字までにしてください。");
			} else {
				return;
			}
		}
		if (${$init->{ng_word}}[0]) {
			foreach (@{$init->{ng_word}}) {
				if ($_ and $message_ins->get_string =~ /$_/) {
					if ($init->{error_mode}) {
						&error("「$_」は使用禁止ワードに設定されています。");
					} else {
						return;
					}
				}
			}
		}
		if ($init->{need_japanese} and $message_ins->get_string !~ /[\x80-\xFF]/) {
			if ($init->{error_mode}) {
				&error("日本語を含まないメッセージは投稿できません。");
			} else {
				return;
			}
		}
		if ($init->{max_link} and $init->{max_link} < $message_ins->check_count('http://')) {
			if ($init->{error_mode}) {
				&error("メッセージにURLを$init->{max_link}個以上書く事はできません。");
			} else {
				return;
			}
		}
	}

	if ($init->{other_link} and $page_ins->check_count('http://')) {
		if ($init->{error_mode}) {
			&error("メッセージ欄以外にURLを書く事はできません。");
		} else {
			return;
		}
	}

	if (!$count_ins->get_string) {
		$count_ins->set_string(1);
	}

	my %query = %{$parser_ins->get_query};
	my $option;
	foreach (sort keys %query) {
		if ($_ =~ /^option(\d+)$/ and $query{$_}) {
			if ($option) {
				$option .= '<>';
			}
			if ($query{"label$1"}) {
				$option .= $query{"label$1"};
			}

			my $option_ins = new webliberty::String($query{$_});
			$option_ins->create_line;

			if ($init->{other_link} and $option_ins->check_count('http://')) {
				if ($init->{error_mode}) {
					&error("メッセージ欄以外にURLを書く事はできません。");
				} else {
					return;
				}
			}

			$option .= $option_ins->get_string;
		}
	}
	if ($agent eq 'mobile') {
		$option = Jcode->new($option, 'sjis')->utf8;
	}

	#重複登録チェック
	opendir(DIR, $init->{logs_dir}) or $basis_ins->error("Read Error : $init->{logs_dir}");
	my @dir = sort { $b <=> $a } readdir(DIR);
	closedir(DIR);

	my $show_file = $init->{logs_dir} . $dir[0];

	if (-s $show_file) {
		my($last_date, $last_message, $last_option, $last_count, $last_page, $last_host);
		open(FH, $show_file) or &error("Read Error : $show_file");
		foreach (reverse <FH>) {
			chomp;
			($last_date, $last_message, $last_option, $last_count, $last_page, $last_host) = split(/\t/);

			last;
		}
		close(FH);

		if ($count_ins->get_string > 1 and $message_ins->get_string eq $last_message and $option eq $last_option and $count_ins->get_string eq $last_count and $page_ins->get_string eq $last_page and $host_ins->get_host eq $last_host) {
			return;
		}
	}

	#データ記録
	my $lock_ins = new webliberty::Lock($init->{lock_file});
	if (!$lock_ins->file_lock) {
		&error('ファイルがロックされています。時間をおいてもう一度投稿してください。');
	}

	my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
	my $log_name = sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $day);

	if (open(FH, ">>$init->{logs_dir}$log_name\.$init->{logs_ext}")) {
		print FH time . "\t" . $message_ins->get_string . "\t" . $option . "\t" . $count_ins->get_string . "\t" . $page_ins->get_string . "\t" . $host_ins->get_host . "\n";
		close(FH);
	} else {
		&error("Write Error : $init->{logs_dir}$log_name\.$init->{logs_ext}");
	}

	my $i;
	opendir(DIR, $init->{logs_dir}) or &error("Read Error : $init->{logs_dir}");
	foreach (sort { $b <=> $a } readdir(DIR)) {
		if ($_ =~ /^(\d\d\d\d\d\d\d\d)\.$init->{logs_ext}$/ and $i++ >= $init->{save_days}) {
			if ($init->{save_message}) {
				my $data;
				open(FH, "$init->{logs_dir}$_") or $basis_ins->error("Read Error : $init->{logs_dir}$_");
				foreach (<FH>) {
					chomp;
					my($date, $message, $option, $count, $page, $host) = split(/\t/);

					if ($message) {
						$data .= "$_\n";
					}
				}
				close(FH);

				if ($data) {
					open(FH, ">$init->{past_dir}$_") or $basis_ins->error("Write Error : $init->{logs_dir}$_");
					print FH $data;
					close(FH);
				}
			}
			unlink("$init->{logs_dir}$_");
		}
	}
	closedir(DIR);

	#総拍手数記録
	if ($init->{count_mode}) {
		&countup;
	}

	$lock_ins->file_unlock;

	#メール通知
	if ($init->{sendmail_mode} and $message_ins->get_string) {
		my $sendmail_ins = new webliberty::Sendmail($init->{sendmail_path});
		foreach (@{$init->{sendmail_list}}) {
			if (!$_) {
				next;
			}

			my $message = $message_ins->get_string;

			foreach my $key (split(/<>/, $option)) {
				$message .= "\n（$key）";
			}
			if ($init->{show_host}) {
				$message .= "\n\nHost : " . $host_ins->get_host;
			}

			my $flag = $sendmail_ins->sendmail(
				send_to => $_,
				subject => $init->{sendmail_subject},
				message => $message
			);
			if (!$flag) {
				&error('メールの送信に失敗しました。');
			}
		}
	}

	return;
}

### 総拍手数記録
sub countup {
	open(FH, $init->{count_file}) or $basis_ins->error("Read Error : $init->{count_file}");
	my $data = <FH>;
	close(FH);

	my($count, $today, $yesterday, $key) = split(/\t/, $data);
	my($sec, $min, $hour, $day) = localtime(time);

	if ($key == $day) {
		$today++;
	} else {
		$yesterday = $today;
		$today     = 1;
	}
	$count++;

	open(FH, ">$init->{count_file}") or $basis_ins->error("Write Error : $init->{count_file}");
	print FH "$count\t$today\t$yesterday\t$day";
	close(FH);

	return;
}

### 送信完了
sub complete {
	my($message, $page);
	if ($agent eq 'mobile') {
		$message = Jcode->new($parser_ins->get_query('message'), 'sjis')->utf8;
		$page    = Jcode->new($parser_ins->get_query('page'), 'sjis')->utf8;
	} else {
		$message = $parser_ins->get_query('message');
		$page    = $parser_ins->get_query('page');
	}

	my $message_ins = new webliberty::String($message);
	my $page_ins    = new webliberty::String($page);

	$message_ins->create_text;
	$page_ins->create_line;

	#表示用データ取得
	my $max = 0;
	open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($agent eq 'mobile') {
			next if ($target eq 'pc');
		} else {
			next if ($target eq 'mobile');
		}

		if ($stat) {
			$max++;
		}
	}
	seek(FH, 0, 0);

	my $show;
	if (!$parser_ins->get_query('id') or (!$init->{second_mode} and $parser_ins->get_query('count') >= 2)) {
		if ($init->{order_mode}) {
			my $count;
			if ($parser_ins->get_query('count')) {
				$count = $parser_ins->get_query('count') - 1;
			} else {
				$count = 0;
			}

			$show = $count % $max + 1 if ($max);
		} else {
			$show = int(rand($max) + 1);
		}
	}

	my($show_explain, $show_text, $show_file, $show_pcskin, $show_mobileskin, $flag, $i);

	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($agent eq 'mobile') {
			next if ($target eq 'pc');
		} else {
			next if ($target eq 'mobile');
		}

		if (!$stat) {
			next;
		}

		if ((!$show and $parser_ins->get_query('id') eq $id) or $show == ++$i) {
			$show_explain    = $explain;
			$show_text       = $text;
			$show_file       = $file;
			$show_pcskin     = $pcskin;
			$show_mobileskin = $mobileskin;

			$flag = 1;

			last;
		}
	}
	close(FH);

	if (!$flag) {
		if (-s $init->{thanks_file}) {
			&error('お礼メッセージを読み出せません。');
		} else {
			&error('お礼メッセージが設定されていません。管理者ページからお礼画面を登録してください。');
		}
	}

	#表示用データ作成
	my $text_ins = new webliberty::String($show_text);
	$text_ins->create_text;
	$text_ins->permit_html;

	my($show_file_start, $show_file_end);
	if ($show_file) {
		my $file_ins = new webliberty::File("$init->{upfile_dir}$show_file");
		my($width, $height) = $file_ins->get_size;

		if ($width > 0 and $height > 0) {
			$show_file = "<img src=\"$init->{upfile_dir}$show_file\" alt=\"$show_file\" width=\"$width\" height=\"$height\" />";
		} else {
			$show_file = "<a href=\"$init->{upfile_dir}$show_file\">$show_file</a>";
		}
	} else {
		$show_file_start = '<!--';
		$show_file_end   = '-->';
	}

	my($show_message_start, $show_message_end);
	if (!$init->{confirm_mode} or !$message_ins->get_string) {
		$show_message_start = '<!--';
		$show_message_end   = '-->';
	}

	my $count;
	if ($parser_ins->get_query('count')) {
		$count = $parser_ins->get_query('count') + 1;
	} else {
		$count = 2;
	}

	my $method;
	if ($ENV{'HTTP_USER_AGENT'} =~ /(J-PHONE|UP\.Browser)/i) {
		$method = 'get';
	} else {
		$method = 'post';
	}

	#お礼画面表示
	my $skin_ins = new webliberty::Skin;
	if ($agent eq 'mobile') {
		if ($show_mobileskin) {
			$skin_ins->parse_skin($init->{skin_mobile_thanks_dir} . $show_mobileskin);
		} else {
			$skin_ins->parse_skin($init->{skin_mobile_thanks});
		}
	} else {
		if ($show_pcskin) {
			$skin_ins->parse_skin($init->{skin_thanks_dir} . $show_pcskin);
		} else {
			$skin_ins->parse_skin($init->{skin_thanks});
		}
	}

	$skin_ins->replace_skin(
		INFO_EXPLAIN       => $show_explain,
		INFO_TEXT          => $text_ins->get_string,
		INFO_FILE          => $show_file,
		INFO_FILE_START    => $show_file_start,
		INFO_FILE_END      => $show_file_end,
		INFO_MESSAGE       => $message_ins->get_string,
		INFO_MESSAGE_START => $show_message_start,
		INFO_MESSAGE_END   => $show_message_end,
		INFO_COUNT         => $count,
		INFO_PAGE          => $page_ins->get_string,
		INFO_ID            => $parser_ins->get_query('id'),
		INFO_METHOD        => $method
	);

	if ($agent eq 'mobile') {
		my($html, $length) = &get_mobile_data($skin_ins->get_data('_all'));

		print "Content-Type: text/html; charset=Shift_JIS\n";
		if ($ENV{'HTTP_USER_AGENT'} =~ /KDDI-|UP\.Browser/i) {
			print "Pragma: no-cache\n";
			print "Cache-Control: no-cache\n\n";
		} else {
			print "Content-Length: $length\n\n";
		}
		print $html;
	} else {
		print $basis_ins->header;
		print $skin_ins->get_data('_all');
	}

	return;
}

### 最大連続拍手数チェック
sub check_limit {
	my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
	my $log_name = sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $day);

	my $host_ins = new webliberty::Host;

	my $flag;
	if (open(FH, "$init->{logs_dir}$log_name\.$init->{logs_ext}")) {
		my $i;
		while (<FH>) {
			chomp;
			my($date, $message, $option, $count, $page, $host) = split(/\t/);

			if (time - $date > $init->{limit_interval} * 60) {
				next;
			}
			if ($host_ins->get_host and $host_ins->get_host eq $host) {
				$i++;
			}

			if ($i >= $init->{limit_count}) {
				$flag = 1;
			}
		}
		close(FH);
	}

	if ($flag) {
		my $message;
		if ($agent eq 'mobile') {
			$message = Jcode->new($parser_ins->get_query('message'), 'sjis')->utf8;
		} else {
			$message = $parser_ins->get_query('message');
		}

		my $message_ins = new webliberty::String($message);
		$message_ins->create_text;

		my($show_message_start, $show_message_end);
		if (!$init->{confirm_mode} or !$message_ins->get_string) {
			$show_message_start = '<!--';
			$show_message_end   = '-->';
		}

		my $skin_ins = new webliberty::Skin;
		if ($agent eq 'mobile') {
			$skin_ins->parse_skin($init->{skin_mobile_limit});
		} else {
			$skin_ins->parse_skin($init->{skin_limit});
		}

		$skin_ins->replace_skin(
			INFO_LIMIT         => $init->{limit_count},
			INFO_MESSAGE       => $message_ins->get_string,
			INFO_MESSAGE_START => $show_message_start,
			INFO_MESSAGE_END   => $show_message_end
		);

		if ($agent eq 'mobile') {
			my($html, $length) = &get_mobile_data($skin_ins->get_data('_all'));

			print "Content-Type: text/html; charset=Shift_JIS\n";
			if ($ENV{'HTTP_USER_AGENT'} =~ /KDDI-|UP\.Browser/i) {
				print "Pragma: no-cache\n";
				print "Cache-Control: no-cache\n\n";
			} else {
				print "Content-Length: $length\n\n";
			}
			print $html;
		} else {
			print $basis_ins->header;
			print $skin_ins->get_data('_all');
		}

		exit;
	}

	return;
}

### エラー表示
sub error {
	my($message) = @_;

	my $skin_ins = new webliberty::Skin;
	if ($agent eq 'mobile') {
		$skin_ins->parse_skin($init->{skin_mobile_error});
	} else {
		$skin_ins->parse_skin($init->{skin_error});
	}

	$skin_ins->replace_skin(
		INFO_ERROR => $message
	);

	if ($agent eq 'mobile') {
		my($html, $length) = &get_mobile_data($skin_ins->get_data('_all'));

		print "Content-Type: text/html; charset=Shift_JIS\n";
		if ($ENV{'HTTP_USER_AGENT'} =~ /KDDI-|UP\.Browser/i) {
			print "Pragma: no-cache\n";
			print "Cache-Control: no-cache\n\n";
		} else {
			print "Content-Length: $length\n\n";
		}
		print $html;
	} else {
		print $basis_ins->header;
		print $skin_ins->get_data('_all');
	}

	exit;
}

### 携帯用データ作成
sub get_mobile_data {
	my($data) = @_;

	$data =~ s/\xEF\xBD\x9E/\xE3\x80\x9C/g;
	$data = Jcode->new($data, 'utf8')->sjis;

	return($data, length($data) + ($data =~ s/\n/\n/g));
}
