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
use webliberty::Cookie;
use webliberty::Lock;
use webliberty::Skin;

require './init.cgi';

#――――― メイン処理 ―――――――――――――――――――――――

my $init = &init::get_init;

my $basis_ins  = new webliberty::Basis;
my $parser_ins = new webliberty::Parser(jcode => $init->{jcode_mode});

if (&check_password) {
	if ($parser_ins->get_query('mode') eq 'logout') {
		&logout;
	} elsif ($parser_ins->get_query('mode') eq 'new') {
		if ($parser_ins->get_query('exec_regist')) {
			&regist;
			&edit;
		} else {
			&form;
		}
	} elsif ($parser_ins->get_query('mode') eq 'edit') {
		if ($parser_ins->get_query('exec_regist')) {
			&regist;
		} elsif ($parser_ins->get_query('exec_del')) {
			&del;
		} elsif ($parser_ins->get_query('exec_order')) {
			&order;
		}
		if ($parser_ins->get_query('exec_form')) {
			&form;
		} else {
			&edit;
		}
	} elsif ($parser_ins->get_query('mode') eq 'confirm') {
		&confirm;
	} elsif ($parser_ins->get_query('mode') eq 'message') {
		if ($parser_ins->get_query('exec_del')) {
			&message_del;
		}
		&message;
	} elsif ($parser_ins->get_query('mode') eq 'page') {
		&page;
	} elsif ($parser_ins->get_query('mode') eq 'date') {
		&date;
	} else {
		&list;
	}
} else {
	&login;
}

exit;

#――――― サブルーチン ――――――――――――――――――――――

### パスワード認証
sub check_password {
	my $cookie_ins = new webliberty::Cookie($init->{cookie_admin}, $init->{des_key});

	my(%query, $admin_pwd);

	if ($parser_ins->get_query) {
		%query = %{$parser_ins->get_query};
	}

	if (exists $query{'admin_pwd'}) {
		$admin_pwd = $parser_ins->get_query('admin_pwd');
	} else {
		$admin_pwd = $cookie_ins->get_cookie('admin_pwd');
	}

	my $flag;

	if ($admin_pwd eq $init->{admin_pwd}) {
		if ($parser_ins->get_query('admin_pwd')) {
			if ($parser_ins->get_query('hold')) {
				$cookie_ins->set_holddays(3650);
			}
			$cookie_ins->set_cookie(
				admin_pwd => $admin_pwd
			);
		}

		$flag = 1;
	}

	return $flag;
}

### ログイン画面
sub login {
	my $message;
	if ($parser_ins->get_query('admin_pwd')) {
		$message = 'パスワードが違います。';
	} else {
		$message = '管理者パスワードを入力してください。';
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_login});

	$skin_ins->replace_skin(
		INFO_TITLE   => $init->{admin_title},
		INFO_PATH    => $init->{script_file},
		INFO_MESSAGE => $message
	);

	print $basis_ins->header;
	print $skin_ins->get_data('login_head');

	my $work_data;
	$work_data  = "\t拍手一覧\n";
	$work_data .= "date\t日時別一覧\n";
	if ($init->{page_mode}) {
		$work_data .= "page\t送信元ページ別一覧\n";
	}
	$work_data .= "message\tメッセージ一覧\n";
	$work_data .= "new\tお礼画面登録\n";
	$work_data .= "edit\tお礼画面管理\n";

	foreach (split(/\n/, $work_data)) {
		my($work_id, $work_name) = split(/\t/);

		print $skin_ins->get_replace_data(
			'login',
			WORK_ID   => $work_id,
			WORK_NAME => $work_name
		);
	}

	print $skin_ins->get_data('login_foot');

	return;
}

### ログアウト
sub logout {
	my $cookie_ins = new webliberty::Cookie($init->{cookie_admin}, $init->{des_key});
	$cookie_ins->set_cookie(
		admin_pwd => ''
	);

	&login;

	return;
}

### お礼画面登録
sub regist {
	my $edit_ins       = new webliberty::String($parser_ins->get_query('edit'));
	my $id_ins         = new webliberty::String($parser_ins->get_query('id'));
	my $stat_ins       = new webliberty::String($parser_ins->get_query('stat'));
	my $target_ins     = new webliberty::String($parser_ins->get_query('target'));
	my $explain_ins    = new webliberty::String($parser_ins->get_query('explain'));
	my $text_ins       = new webliberty::String($parser_ins->get_query('text'));
	my $pcskin_ins     = new webliberty::String($parser_ins->get_query('pcskin'));
	my $mobileskin_ins = new webliberty::String($parser_ins->get_query('mobileskin'));

	$edit_ins->create_line;
	$id_ins->create_line;
	$stat_ins->create_number;
	$target_ins->create_line;
	$explain_ins->create_line;
	$text_ins->create_text;
	$pcskin_ins->create_line;
	$mobileskin_ins->create_line;

	if (!$init->{use_stat}) {
		$stat_ins->set_string(1);
	}
	if (!$text_ins->get_string) {
		&error('テキストが入力されていません。');
	}

	if ($id_ins->get_string =~ /[^\w\d\-\_]/) {
		&error("IDは半角英数字で指定してください。");
	}
	if ($init->{use_file} and $parser_ins->get_query('file')) {
		my $file_ins  = new webliberty::File($parser_ins->get_filename('file'));
		my $file_name = $file_ins->get_name . '.' . $file_ins->get_ext;

		if ($file_ins->get_name =~ /[^\w\d\-\_]/) {
			&error("ファイル名は半角英数字で指定してください。");
		}
	}

	my $lock_ins = new webliberty::Lock($init->{lock_file});
	if (!$lock_ins->file_lock) {
		&error('ファイルがロックされています。時間をおいてもう一度登録してください。');
	}

	if ($edit_ins->get_string) {
		my $file_name;
		if ($init->{use_file}) {
			#ファイル名取得
			my $org_file;
			open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
			while (<FH>) {
				chomp;
				my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

				if ($edit_ins->get_string eq $id) {
					$org_file = $file;
				}
			}
			close(FH);

			#アップロードファイル保存
			if ($parser_ins->get_query('delfile')) {
				unlink("$init->{upfile_dir}$org_file");
			} elsif ($parser_ins->get_query('file')) {
				unlink("$init->{upfile_dir}$org_file");

				my $file_ins = new webliberty::File($parser_ins->get_filename('file'));
				$file_name = $file_ins->get_name . '.' . $file_ins->get_ext;

				if ($file_ins->get_name =~ /[^\w\d\-\_]/) {
					$lock_ins->file_unlock;
					&error("ファイル名は半角英数字で指定してください。");
				}
				if (-e "$init->{upfile_dir}$file_name") {
					$lock_ins->file_unlock;
					&error("$file_nameは既に存在します。ファイル名を変更してアップロードしてください。");
				}

				open(FH, ">$init->{upfile_dir}$file_name") or &error("Write Error : $init->{upfile_dir}$file_name");
				binmode(FH);
				print FH $parser_ins->get_filedata('file');
				close(FH);
			} else {
				$file_name = $org_file;
			}
		}

		#お礼画面編集
		my($new_data, $flag);

		open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
		while (<FH>) {
			chomp;
			my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

			if ($edit_ins->get_string eq $id) {
				if ($id_ins->get_string) {
					$id = $id_ins->get_string;
				}

				$new_data .= "$id\t" . $stat_ins->get_string . "\t" . $target_ins->get_string . "\t" . $explain_ins->get_string . "\t" . $text_ins->get_string . "\t$file_name\t" . $pcskin_ins->get_string . "\t" . $mobileskin_ins->get_string . "\n";

				$flag = 1;
			} else {
				if ($id_ins->get_string eq $id) {
					$lock_ins->file_unlock;
					&error("そのIDは既に使用されています。");
				} else {
					$new_data .= "$_\n";
				}
			}
		}
		close(FH);

		if (!$flag) {
			$lock_ins->file_unlock;
			&error('該当するお礼画面はありません。');
		}

		open(FH, ">$init->{thanks_file}") or &error("Write Error : $init->{thanks_file}");
		print FH $new_data;
		close(FH);
	} else {
		#ID重複チェック
		my $new_id;
		if ($id_ins->get_string) {
			$new_id = $id_ins->get_string;
		} else {
			$new_id = time;
		}
		open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
		while (<FH>) {
			chomp;
			my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

			if ($new_id eq $id) {
				$lock_ins->file_unlock;
				if ($init->{use_id}) {
					&error("そのIDは既に使用されています。");
				} else {
					&error("IDの発行に失敗しました。");
				}
			}
		}
		close(FH);

		#アップロードファイル保存
		my $file_name;
		if ($init->{use_file} and $parser_ins->get_query('file')) {
			my $file_ins = new webliberty::File($parser_ins->get_filename('file'));
			$file_name = $file_ins->get_name . '.' . $file_ins->get_ext;

			if ($file_ins->get_name =~ /[^\w\d\-\_]/) {
				$lock_ins->file_unlock;
				&error("ファイル名は半角英数字で指定してください。");
			}
			if (-e "$init->{upfile_dir}$file_name") {
				$lock_ins->file_unlock;
				&error("$file_nameは既に存在します。ファイル名を変更してアップロードしてください。");
			}

			open(FH, ">$init->{upfile_dir}$file_name") or &error("Write Error : $init->{upfile_dir}$file_name");
			binmode(FH);
			print FH $parser_ins->get_filedata('file');
			close(FH);
		}

		#お礼画面登録
		open(FH, ">>$init->{thanks_file}") or &error("Write Error : $init->{thanks_file}");
		print FH "$new_id\t" . $stat_ins->get_string . "\t" . $target_ins->get_string . "\t" . $explain_ins->get_string . "\t" . $text_ins->get_string . "\t$file_name\t" . $pcskin_ins->get_string . "\t" . $mobileskin_ins->get_string . "\n";
		close(FH);
	}

	$lock_ins->file_unlock;

	return;
}

### お礼画面一覧
sub edit {
	my $message;
	if ($parser_ins->get_query('mode') eq 'new') {
		$message = 'お礼画面を新規に登録しました。';
	} elsif ($parser_ins->get_query('exec_regist')) {
		$message = 'お礼画面を編集しました。';
	} elsif ($parser_ins->get_query('exec_del')) {
		$message = 'お礼画面を削除しました。';
	} else {
		$message = 'お礼画面を選択し、<em>編集ボタン</em>か<em>削除ボタン</em>を押してください。';
	}

	my($id_start, $id_end);
	if (!$init->{use_id}) {
		$id_start = '<!--';
		$id_end   = '-->';
	}

	my($stat_start, $stat_end);
	if (!$init->{use_stat}) {
		$stat_start = '<!--';
		$stat_end   = '-->';
	}

	my($target_start, $target_end);
	if (!$init->{use_target}) {
		$target_start = '<!--';
		$target_end   = '-->';
	}

	my($explain_start, $explain_end);
	if (!$init->{use_explain}) {
		$explain_start = '<!--';
		$explain_end   = '-->';
	}

	my($file_start, $file_end);
	if (!$init->{use_file}) {
		$file_start = '<!--';
		$file_end   = '-->';
	}

	my($pcskin_start, $pcskin_end);
	if (!$init->{use_skin_pc}) {
		$pcskin_start = '<!--';
		$pcskin_end   = '-->';
	}

	my($mobileskin_start, $mobileskin_end);
	if (!$init->{use_skin_mobile}) {
		$mobileskin_start = '<!--';
		$mobileskin_end   = '-->';
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_edit});
	$skin_ins->parse_skin($init->{skin_admin_footer});

	$skin_ins->replace_skin(
		INFO_TITLE   => $init->{admin_title},
		INFO_SCRIPT  => $init->{script_file},
		INFO_MESSAGE => $message
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	print $skin_ins->get_replace_data(
		'edit_head',
		EDIT_ID_START         => $id_start,
		EDIT_ID_END           => $id_end,
		EDIT_STAT_START       => $stat_start,
		EDIT_STAT_END         => $stat_end,
		EDIT_TARGET_START     => $target_start,
		EDIT_TARGET_END       => $target_end,
		EDIT_EXPLAIN_START    => $explain_start,
		EDIT_EXPLAIN_END      => $explain_end,
		EDIT_FILE_START       => $file_start,
		EDIT_FILE_END         => $file_end,
		EDIT_PCSKIN_START     => $pcskin_start,
		EDIT_PCSKIN_END       => $pcskin_end,
		EDIT_MOBILESKIN_START => $mobileskin_start,
		EDIT_MOBILESKIN_END   => $mobileskin_end
	);

	open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($stat) {
			$stat = '使用';
		} else {
			$stat = '未使用';
		}

		if ($target eq 'pc') {
			$target = 'PC専用';
		} elsif ($target eq 'mobile') {
			$target = '携帯専用';
		} else {
			$target = 'すべて';
		}

		my $text_ins = new webliberty::String($text);
		$text_ins->create_line;
		$text_ins->trim_string(100, '...');

		if ($file) {
			$file = "<a href=\"$init->{upfile_dir}$file\">$file</a>";
		}

		print $skin_ins->get_replace_data(
			'edit',
			EDIT_ID               => $id,
			EDIT_ID_START         => $id_start,
			EDIT_ID_END           => $id_end,
			EDIT_STAT             => $stat,
			EDIT_STAT_START       => $stat_start,
			EDIT_STAT_END         => $stat_end,
			EDIT_TARGET           => $target,
			EDIT_TARGET_START     => $target_start,
			EDIT_TARGET_END       => $target_end,
			EDIT_EXPLAIN          => $explain,
			EDIT_EXPLAIN_START    => $explain_start,
			EDIT_EXPLAIN_END      => $explain_end,
			EDIT_TEXT             => $text_ins->get_string,
			EDIT_FILE             => $file,
			EDIT_FILE_START       => $file_start,
			EDIT_FILE_END         => $file_end,
			EDIT_PCSKIN_START     => $pcskin_start,
			EDIT_PCSKIN_END       => $pcskin_end,
			EDIT_MOBILESKIN_START => $mobileskin_start,
			EDIT_MOBILESKIN_END   => $mobileskin_end
		);
	}
	close(FH);

	print $skin_ins->get_replace_data(
		'edit_foot',
		EDIT_ID_START         => $id_start,
		EDIT_ID_END           => $id_end,
		EDIT_STAT_START       => $stat_start,
		EDIT_STAT_END         => $stat_end,
		EDIT_TARGET_START     => $target_start,
		EDIT_TARGET_END       => $target_end,
		EDIT_EXPLAIN_START    => $explain_start,
		EDIT_EXPLAIN_END      => $explain_end,
		EDIT_FILE_START       => $file_start,
		EDIT_FILE_END         => $file_end,
		EDIT_PCSKIN_START     => $pcskin_start,
		EDIT_PCSKIN_END       => $pcskin_end,
		EDIT_MOBILESKIN_START => $mobileskin_start,
		EDIT_MOBILESKIN_END   => $mobileskin_end
	);

	print $skin_ins->get_data('footer');

	return;
}

### お礼画面確認
sub confirm {
	my($show_target, $show_explain, $show_text, $show_file, $show_pcskin, $show_mobileskin, $flag);

	open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($parser_ins->get_query('id') eq $id) {
			$show_target     = $target;
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
		&error('お礼メッセージを読み出せません。');
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

	#お礼画面表示
	my $skin_ins = new webliberty::Skin;
	if ($show_target eq 'mobile') {
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
		INFO_MESSAGE       => '',
		INFO_MESSAGE_START => '<!--',
		INFO_MESSAGE_END   => '-->',
		INFO_COUNT         => 1,
		INFO_PAGE          => '',
		INFO_ID            => $parser_ins->get_query('id'),
		INFO_METHOD        => 'post'
	);

	if ($show_target eq 'mobile') {
		my($html, $length) = &get_mobile_data($skin_ins->get_data('_all'));

		print "Content-Type: text/html; charset=Shift_JIS\n";
		print "Content-Length: $length\n\n";
		print $html;
	} else {
		print $basis_ins->header;
		print $skin_ins->get_data('_all');
	}

	return;
}

### お礼画面削除
sub del {
	if (!$parser_ins->get_query('del')) {
		&error('削除したいお礼画面を選択してください。');
	}

	my $lock_ins = new webliberty::Lock($init->{lock_file});
	if (!$lock_ins->file_lock) {
		&error('ファイルがロックされています。時間をおいてもう一度登録してください。');
	}

	my($new_data, $flag, $i);

	open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($parser_ins->get_query('del') =~ /(^|\n)$id(\n|$)/) {
			if ($file) {
				unlink("$init->{upfile_dir}$file");
			}

			$flag = 1;
		} else {
			$new_data .= "$_\n";
		}
	}
	close(FH);

	if (!$flag) {
		$lock_ins->file_unlock;
		&error('指定されたお礼画面は存在しません。');
	}

	open(FH, ">$init->{thanks_file}") or &error("Write Error : $init->{thanks_file}");
	print FH $new_data;
	close(FH);

	$lock_ins->file_unlock;

	return;
}

### お礼画面並び替え
sub order {
	if (!$parser_ins->get_query('from') or !$parser_ins->get_query('to')) {
		&error('移動元と移動先を選択してください。');
	}

	my $lock_ins = new webliberty::Lock($init->{lock_file});
	if (!$lock_ins->file_lock) {
		&error('ファイルがロックされています。時間をおいてもう一度登録してください。');
	}

	my($to_data, $new_data, $i);

	open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($parser_ins->get_query('from') eq $id) {
			$to_data = $_;
		}
	}
	seek(FH, 0, 0);
	while (<FH>) {
		chomp;
		my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

		if ($parser_ins->get_query('from') ne $id) {
			$new_data .= "$_\n";
		}
		if ($parser_ins->get_query('to') eq $id) {
			$new_data .= "$to_data\n";
		}
	}
	close(FH);

	open(FH, ">$init->{thanks_file}") or &error("Write Error : $init->{thanks_file}");
	print FH $new_data;
	close(FH);

	$lock_ins->file_unlock;

	return;
}

### お礼画面登録フォーム表示
sub form {
	my($form_mode, $form_id, $form_stat, $form_target, $form_explain, $form_text, $form_pcskin, $form_mobileskin, $form_file, $form_new_start, $form_new_end, $form_edit_start, $form_edit_end);

	if ($parser_ins->get_query('mode') eq 'edit') {
		if (!$parser_ins->get_query('edit')) {
			&error('編集したいお礼画面を選択してください。');
		}

		$form_new_start = '<!--';
		$form_new_end   = '-->';

		$form_mode = 'edit';

		open(FH, $init->{thanks_file}) or &error("Read Error : $init->{thanks_file}");
		while (<FH>) {
			chomp;
			my($id, $stat, $target, $explain, $text, $file, $pcskin, $mobileskin) = split(/\t/);

			if ($parser_ins->get_query('edit') eq $id) {
				my $text_ins = new webliberty::String($text);
				$text_ins->create_text;

				$form_id         = $id;
				$form_stat       = $stat;
				$form_target     = $target;
				$form_explain    = $explain;
				$form_text       = $text_ins->create_plain;
				$form_pcskin     = $pcskin;
				$form_mobileskin = $mobileskin;

				if ($file) {
					$form_file = "<input type=\"checkbox\" name=\"delfile\" id=\"delfile_checkbox\" value=\"on\"> <label for=\"delfile_checkbox\">$fileを削除</label>";
				}

				last;
			}
		}
		close(FH);
	} else {
		$form_edit_start = '<!--';
		$form_edit_end   = '-->';

		$form_mode = 'new';

		$form_stat = 1;
	}

	my($form_id_start, $form_id_end);
	if (!$init->{use_id}) {
		$form_id_start = '<!--';
		$form_id_end   = '-->';
	}

	my($form_stat_start, $form_stat_end);
	if ($init->{use_stat}) {
		if ($form_stat) {
			$form_stat = ' checked="checked"';
		} else {
			$form_stat = '';
		}
	} else {
		$form_stat_start = '<!--';
		$form_stat_end   = '-->';
	}

	my($form_target_start, $form_target_end);
	if ($init->{use_target}) {
		if ($form_target eq 'pc') {
			$form_target = '<option value="">すべて</option><option value="pc" selected="selected">PC専用</option><option value="mobile">携帯専用</option>';
		} elsif ($form_target eq 'mobile') {
			$form_target = '<option value="">すべて</option><option value="pc">PC専用</option><option value="mobile" selected="selected">携帯専用</option>';
		} else {
			$form_target = '<option value="">すべて</option><option value="pc">PC専用</option><option value="mobile">携帯専用</option>';
		}
		$form_target = "<select name=\"target\" xml:lang=\"ja\" lang=\"ja\">$form_target</select>";
	} else {
		$form_target_start = '<!--';
		$form_target_end   = '-->';
	}

	my($form_explain_start, $form_explain_end);
	if (!$init->{use_explain}) {
		$form_explain_start = '<!--';
		$form_explain_end   = '-->';
	}

	my($form_file_start, $form_file_end);
	if (!$init->{use_file}) {
		$form_file_start = '<!--';
		$form_file_end   = '-->';
	}

	my($form_pcskin_start, $form_pcskin_end);
	if ($init->{use_skin_pc}) {
		my $form_list;

		opendir(DIR, $init->{skin_thanks_dir}) or $basis_ins->error("Read Error : $init->{skin_thanks_dir}");
		foreach (sort { $b <=> $a } readdir(DIR)) {
			if ($_ !~ /^\w+\.$init->{skin_exit}$/) {
				next;
			}

			if ($form_pcskin eq $_) {
				$form_list .= "<option value=\"$_\" selected=\"selected\">$_</option>";
			} else {
				$form_list .= "<option value=\"$_\">$_</option>";
			}
		}
		closedir(DIR);

		$form_pcskin = "<select name=\"pcskin\" xml:lang=\"ja\" lang=\"ja\"><option value=\"\">標準スキン</option>$form_list</select>";
	} else {
		$form_pcskin_start = '<!--';
		$form_pcskin_end   = '-->';
	}

	my($form_mobileskin_start, $form_mobileskin_end);
	if ($init->{use_skin_mobile}) {
		my $form_list;

		opendir(DIR, $init->{skin_mobile_thanks_dir}) or $basis_ins->error("Read Error : $init->{skin_mobile_thanks_dir}");
		foreach (sort { $b <=> $a } readdir(DIR)) {
			if ($_ !~ /^\w+\.$init->{skin_exit}$/) {
				next;
			}

			if ($form_mobileskin eq $_) {
				$form_list .= "<option value=\"$_\" selected=\"selected\">$_</option>";
			} else {
				$form_list .= "<option value=\"$_\">$_</option>";
			}
		}
		closedir(DIR);

		$form_mobileskin = "<select name=\"mobileskin\" xml:lang=\"ja\" lang=\"ja\"><option value=\"\">標準スキン</option>$form_list</select>";
	} else {
		$form_mobileskin_start = '<!--';
		$form_mobileskin_end   = '-->';
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_form});
	$skin_ins->parse_skin($init->{skin_admin_footer});
	$skin_ins->replace_skin(
		INFO_TITLE  => $init->{admin_title},
		INFO_SCRIPT => $init->{script_file}
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	print $skin_ins->get_replace_data(
		'form',
		FORM_MODE             => $parser_ins->get_query('mode'),
		FORM_EDIT             => $parser_ins->get_query('edit'),
		FORM_ID               => $form_id,
		FORM_ID_START         => $form_id_start,
		FORM_ID_END           => $form_id_end,
		FORM_STAT             => $form_stat,
		FORM_STAT_START       => $form_stat_start,
		FORM_STAT_END         => $form_stat_end,
		FORM_TARGET           => $form_target,
		FORM_TARGET_START     => $form_target_start,
		FORM_TARGET_END       => $form_target_end,
		FORM_EXPLAIN          => $form_explain,
		FORM_EXPLAIN_START    => $form_explain_start,
		FORM_EXPLAIN_END      => $form_explain_end,
		FORM_TEXT             => $form_text,
		FORM_FILE             => $form_file,
		FORM_FILE_START       => $form_file_start,
		FORM_FILE_END         => $form_file_end,
		FORM_PCSKIN           => $form_pcskin,
		FORM_PCSKIN_START     => $form_pcskin_start,
		FORM_PCSKIN_END       => $form_pcskin_end,
		FORM_MOBILESKIN       => $form_mobileskin,
		FORM_MOBILESKIN_START => $form_mobileskin_start,
		FORM_MOBILESKIN_END   => $form_mobileskin_end,
		FORM_NEW_START        => $form_new_start,
		FORM_NEW_END          => $form_new_end,
		FORM_EDIT_START       => $form_edit_start,
		FORM_EDIT_END         => $form_edit_end
	);

	print $skin_ins->get_data('footer');

	return;
}

### メッセージ削除
sub message_del {
	if (!$parser_ins->get_query('del')) {
		&error('削除したいメッセージを選択してください。');
	}

	foreach my $del (split(/\n/, $parser_ins->get_query('del'))) {
		my($sec, $min, $hour, $day, $mon, $year, $week) = localtime($del);
		my $file = sprintf("%04d%02d%02d\.$init->{logs_ext}", $year + 1900, $mon + 1, $day);

		if (-e "$init->{logs_dir}$file") {
			$file = "$init->{logs_dir}$file";
		} else {
			$file = "$init->{past_dir}$file";
		}

		my($new_data, $flag);

		open(FH, $file) or $basis_ins->error("Read Error : $file");
		foreach (reverse <FH>) {
			chomp;
			my($date, $message, $option, $count, $page, $host) = split(/\t/);

			if ($del == $date) {
				$flag = 1;
			} else {
				$new_data .= "$_\n";
			}
		}
		close(FH);

		if (!$flag) {
			&error('該当するメッセージはありません。');
		}

		open(FH, ">$file") or &error("Write Error : $file");
		print FH $new_data;
		close(FH);
	}

	return;
}

### メッセージ一覧表示
sub message {
	my $message;
	if ($parser_ins->get_query('exec_del')) {
		$message = 'メッセージを削除しました。';
	} else {
		$message = '送信されたメッセージは以下のとおりです。';
	}

	opendir(DIR, $init->{logs_dir}) or $basis_ins->error("Read Error : $init->{logs_dir}");
	my @dir = sort { $b <=> $a } readdir(DIR);
	closedir(DIR);

	opendir(DIR, $init->{past_dir}) or $basis_ins->error("Read Error : $init->{past_dir}");
	my @past = sort { $b <=> $a } readdir(DIR);
	closedir(DIR);

	my($host_start, $host_end);
	if (!$init->{show_host}) {
		$host_start = '<!--';
		$host_end   = '-->';
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_message});
	$skin_ins->parse_skin($init->{skin_admin_footer});

	$skin_ins->replace_skin(
		INFO_MESSAGE      => $message,
		INFO_TITLE        => $init->{admin_title},
		INFO_SCRIPT       => $init->{script_file},
		MESSGE_HOST_START => $host_start,
		MESSGE_HOST_END   => $host_end
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	print $skin_ins->get_data('message_head');

	my $start = $parser_ins->get_query('page') * $init->{message_size};
	my $end   = $start + $init->{message_size};

	my $i;

	foreach my $entry (@dir, @past) {
		if ($entry !~ /^(\d\d\d\d\d\d\d\d)\.$init->{logs_ext}$/) {
			next;
		}

		my $file;
		if (-e "$init->{logs_dir}$entry") {
			$file = "$init->{logs_dir}$entry";
		} else {
			$file = "$init->{past_dir}$entry";
		}

		open(FH, $file) or $basis_ins->error("Read Error : $file");
		foreach (reverse <FH>) {
			chomp;
			my($date, $message, $option, $count, $page, $host) = split(/\t/);

			if (!$message) {
				next;
			}

			$i++;
			if ($i <= $start) {
				next;
			}
			if ($i > $end) {
				next;
			}

			my($sec, $min, $hour, $day, $mon, $year, $week) = localtime($date);

			$year = sprintf("%02d", $year + 1900);
			$mon  = sprintf("%02d", $mon + 1);
			$day  = sprintf("%02d", $day);
			$hour = sprintf("%02d", $hour);
			$min  = sprintf("%02d", $min);

			my $options;
			foreach my $key (split(/<>/, $option)) {
				if ($options) {
					$options .= '<br />';
				}
				$options .= $key;
			}

			print $skin_ins->get_replace_data(
				'message',
				RESULT_ID      => $date,
				RESULT_YEAR    => $year,
				RESULT_MONTH   => $mon,
				RESULT_DAY     => $day,
				RESULT_HOUR    => $hour,
				RESULT_MINUTE  => $min,
				RESULT_MESSAGE => $message,
				RESULT_OPTION  => $options,
				RESULT_PAGE    => $page,
				RESULT_HOST    => $host
			);
		}
		close(FH);
	}

	print $skin_ins->get_data('message_foot');

	my $page_list;
	foreach (0 .. int(($i - 1) / $init->{message_size})) {
		if ($_ == $parser_ins->get_query('page')) {
			$page_list .= "<option value=\"$_\" selected=\"selected\">ページ" . ($_ + 1) . "</option>";
		} else {
			$page_list .= "<option value=\"$_\">ページ" . ($_ + 1) . "</option>";
		}
	}
	print $skin_ins->get_replace_data(
		'page',
		PAGE_LIST => $page_list
	);

	print $skin_ins->get_data('footer');

	return;
}

### 送信元ページ別一覧
sub page {
	opendir(DIR, $init->{logs_dir}) or $basis_ins->error("Read Error : $init->{logs_dir}");
	my @dir = sort { $b <=> $a } readdir(DIR);
	closedir(DIR);

	my(%page, $page_cnt);

	foreach my $entry (@dir) {
		if ($entry !~ /^(\d\d\d\d\d\d\d\d)\.$init->{logs_ext}$/) {
			next;
		}

		open(FH, "$init->{logs_dir}$entry") or $basis_ins->error("Read Error : $init->{logs_dir}$entry");
		while (<FH>) {
			chomp;
			my($date, $message, $option, $count, $page, $host) = split(/\t/);

			if (!$page) {
				$page = 'ページ指定なし';
			}

			$page{$page}++;
		}
		close(FH);
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_page});
	$skin_ins->parse_skin($init->{skin_admin_footer});

	$skin_ins->replace_skin(
		INFO_TITLE  => $init->{admin_title},
		INFO_SCRIPT => $init->{script_file}
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	print $skin_ins->get_data('page_head');

	foreach (sort { $page{$b} <=> $page{$a} } keys %page) {
		print $skin_ins->get_replace_data(
			'page',
			RESULT_PAGE  => $_,
			RESULT_COUNT => $page{$_},
			RESULT_GRAPH => int($page{$_} / $init->{cutdown_page}) || 0
		);
	}

	print $skin_ins->get_data('page_foot');

	print $skin_ins->get_data('footer');

	return;
}

### 日時別一覧表示
sub date {
	#ログファイル解析
	opendir(DIR, $init->{logs_dir}) or $basis_ins->error("Read Error : $init->{logs_dir}");
	my @dir = sort { $b <=> $a } readdir(DIR);
	closedir(DIR);

	my(%day, %hour, $day_cnt, $hour_cnt);

	foreach my $entry (@dir) {
		if ($entry !~ /^(\d\d\d\d\d\d\d\d)\.$init->{logs_ext}$/) {
			next;
		}

		open(FH, "$init->{logs_dir}$entry") or $basis_ins->error("Read Error : $init->{logs_dir}$entry");
		while (<FH>) {
			chomp;
			my($date, $message, $option, $count, $page, $host) = split(/\t/);

			if ($date) {
				my($sec, $min, $hour, $day, $mon, $year, $week) = localtime($date);
				my $day = sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $day);

				$day{$day}++;
				$hour{$hour}++;
			}
		}
		close(FH);
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_date});
	$skin_ins->parse_skin($init->{skin_admin_footer});

	$skin_ins->replace_skin(
		INFO_TITLE  => $init->{admin_title},
		INFO_SCRIPT => $init->{script_file}
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	#日付別一覧
	print $skin_ins->get_data('day_head');

	foreach (sort { $a <=> $b } keys %day) {
		my($year, $month, $day);
		if ($_ =~ /^(\d\d\d\d)(\d\d)(\d\d)$/) {
			$year  = $1;
			$month = $2;
			$day   = $3;
		}

		print $skin_ins->get_replace_data(
			'day',
			RESULT_YEAR  => $year,
			RESULT_MONTH => $month,
			RESULT_DAY   => $day,
			RESULT_COUNT => $day{$_},
			RESULT_GRAPH => int($day{$_} / $init->{cutdown_date}) || 0
		);
	}

	print $skin_ins->get_data('day_foot');

	#時間別一覧
	print $skin_ins->get_data('hour_head');

	foreach (0 .. 23) {
		print $skin_ins->get_replace_data(
			'hour',
			RESULT_HOUR  => $_,
			RESULT_COUNT => $hour{$_} || 0,
			RESULT_GRAPH => int($hour{$_} / $init->{cutdown_date}) || 0
		);
	}

	print $skin_ins->get_data('hour_foot');

	print $skin_ins->get_data('footer');

	return;
}

### 拍手一覧表示
sub list {
	my $show_file;
	if ($parser_ins->get_query('date')) {
		$show_file = $init->{logs_dir} . $parser_ins->get_query('date') . '.' . $init->{logs_ext};
	} else {
		my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
		$show_file = sprintf("$init->{logs_dir}%04d%02d%02d\.$init->{logs_ext}", $year + 1900, $mon + 1, $day);

		if (!-e $show_file) {
			open(FH, ">$show_file") or &error("Write Error : $show_file");
			close(FH);
		}
	}

	#ログファイル解析
	my(%page, %clap, %count, %pre, %message, $clap);

	open(FH, $show_file) or &error("Read Error : $show_file");
	while (<FH>) {
		chomp;
		my($date, $message, $option, $count, $page, $host) = split(/\t/);

		$page{$page}++;

		if ($parser_ins->get_query('page') and $parser_ins->get_query('page') ne $page) {
			next;
		}

		my($sec, $min, $hour, $day, $mon, $year, $week) = localtime($date);
		my $date = sprintf("%02d:%02d", $hour, $min);

		$clap{$hour}++;

		if ($count > 1 and $count <= $pre{$host}) {
			$count = $pre{$host} + 1;
		}
		$count{$count}++;

		$pre{$host} = $count;

		if ($message or $option) {
			if ($message) {
				$message .= '<br />';
			}

			foreach my $key (split(/<>/, $option)) {
				$message .= "（$key）<br />";
			}

			if ($page) {
				$message = "<strong>$page</strong><br />$message";
			}

			$message .= "time $date";
			if ($init->{show_host}) {
				$message .= " from $host";
			}

			if ($message{$hour}) {
				$message{$hour} .= '<hr />';
			}
			$message{$hour} .= $message;
		}

		$clap++;
	}
	close(FH);

	#総拍手数取得
	my($count_start, $count_end, $count_sum, $count_today, $count_yesterday, $key);

	if ($init->{count_mode}) {
		open(FH, $init->{count_file}) or $basis_ins->error("Read Error : $init->{count_file}");
		my $data = <FH>;
		close(FH);

		($count_sum, $count_today, $count_yesterday, $key) = split(/\t/, $data);
		my($sec, $min, $hour, $day) = localtime(time);

		if ($key != $day) {
			$count_yesterday = $count_today;
			$count_today     = 0;
		}
	} else {
		$count_start = '<!--';
		$count_end   = '-->';
	}

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_admin_header});
	$skin_ins->parse_skin($init->{skin_admin_list});
	$skin_ins->parse_skin($init->{skin_admin_footer});

	$skin_ins->replace_skin(
		INFO_TITLE  => $init->{admin_title},
		INFO_SCRIPT => $init->{script_file}
	);

	print $basis_ins->header;
	print $skin_ins->get_data('header');
	print &work($skin_ins);

	#拍手一覧
	my($sec, $min, $hour, $day, $mon, $year, $week) = localtime(time);
	my $today_file = sprintf("$init->{logs_dir}%04d%02d%02d\.$init->{logs_ext}", $year + 1900, $mon + 1, $day);

	my $show_date;
	if ($show_file eq $today_file) {
		$show_date = (localtime(time))[2];
	} else {
		$show_date = 23;
	}

	my($page_list, $page_list_start, $page_list_end);
	foreach (sort { $page{$b} <=> $page{$a} } keys %page) {
		if ($_) {
			if ($parser_ins->get_query('page') eq $_) {
				$page_list .= "<option value=\"$_\" selected=\"selected\">$_（$page{$_}回）</option>";
			} else {
				$page_list .= "<option value=\"$_\">$_（$page{$_}回）</option>";
			}
		}
	}
	if (!$page_list) {
		$page_list_start = '<!--';
		$page_list_end   = '-->';
	}

	print $skin_ins->get_replace_data(
		'list_head',
		LIST_CLAP            => $clap || 0,
		LIST_DATE            => $parser_ins->get_query('date'),
		LIST_PAGE            => $page_list,
		LIST_PAGE_START      => $page_list_start,
		LIST_PAGE_END        => $page_list_end,
		LIST_COUNT_SUM       => $count_sum || 0,
		LIST_COUNT_TODAY     => $count_today || 0,
		LIST_COUNT_YESTERDAY => $count_yesterday || 0,
		LIST_COUNT_START     => $count_start,
		LIST_COUNT_END       => $count_end
	);

	foreach (0 .. 23) {
		if ($_ > $show_date) {
			last;
		}
		if (!$init->{show_void} and !$clap{$_}) {
			next;
		}

		print $skin_ins->get_replace_data(
			'list',
			RESULT_HOUR    => $_,
			RESULT_COUNT   => $clap{$_} || 0,
			RESULT_GRAPH   => int($clap{$_} / $init->{cutdown_list}) || 0,
			RESULT_MESSAGE => $message{$_}
		);
	}

	print $skin_ins->get_replace_data(
		'list_foot',
		LIST_CLAP            => $clap || 0,
		LIST_COUNT_SUM       => $count_sum || 0,
		LIST_COUNT_TODAY     => $count_today || 0,
		LIST_COUNT_YESTERDAY => $count_yesterday || 0,
		LIST_COUNT_START     => $count_start,
		LIST_COUNT_END       => $count_end
	);

	#送信回数一覧
	print $skin_ins->get_data('count_head');

	my $prev = 0;
	foreach (sort { $b <=> $a } keys %count) {
		my $clap = $count{$_} - $prev;

		$prev = $count{$_};

		$count{$_} = $clap;
	}

	foreach (sort { $a <=> $b } keys %count) {
		if (!$count{$_}) {
			next;
		}

		print $skin_ins->get_replace_data(
			'count',
			RESULT_CLAP  => $_,
			RESULT_COUNT => $count{$_},
			RESULT_GRAPH => int($count{$_} / $init->{cutdown_list}) || 0
		);
	}

	print $skin_ins->get_data('count_foot');

	print $skin_ins->get_data('footer');

	return;
}

### 解析フォーム出力
sub work {
	my($skin_ins) = @_;

	my $skin_data = $skin_ins->get_data('work_head');

	my $work_data;
	$work_data  = "\t拍手一覧\n";
	$work_data .= "date\t日時別一覧\n";
	if ($init->{page_mode}) {
		$work_data .= "page\t送信元ページ別一覧\n";
	}
	$work_data .= "message\tメッセージ一覧\n";
	$work_data .= "new\tお礼画面登録\n";
	$work_data .= "edit\tお礼画面管理\n";
	$work_data .= "logout\tログアウト\n";

	foreach (split(/\n/, $work_data)) {
		my($work_id, $work_name) = split(/\t/);

		if ($parser_ins->get_query('mode') eq $work_id) {
			$skin_data .= $skin_ins->get_replace_data(
				'work_selected',
				WORK_ID   => $work_id,
				WORK_NAME => $work_name
			);
		} else {
			$skin_data .= $skin_ins->get_replace_data(
				'work',
				WORK_ID   => $work_id,
				WORK_NAME => $work_name
			);
		}
	}

	my($work_date, $work_date_start, $work_date_end);
	if ($parser_ins->get_query('mode')) {
		$work_date_start = '<!--';
		$work_date_end   = '-->';
	} else {
		my($sec, $min, $hour, $day, $mon, $year, $week) = localtime(time);
		my $today = sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $day);

		opendir(DIR, $init->{logs_dir}) or $basis_ins->error("Read Error : $init->{logs_dir}");
		foreach my $entry (sort { $b <=> $a } readdir(DIR)) {
			if ($entry =~ /^(\d\d\d\d)(\d\d)(\d\d)\.(\w+)$/ and $4 eq $init->{logs_ext} and ($today eq "$1$2$3" or -s "$init->{logs_dir}$entry")) {
				if ($parser_ins->get_query('date') eq "$1$2$3") {
					$work_date .= "<option value=\"$1$2$3\" selected=\"selected\">$1/$2/$3の拍手</option>";
				} else {
					$work_date .= "<option value=\"$1$2$3\">$1/$2/$3の拍手</option>";
				}
			}
		}
		closedir(DIR);
	}

	$skin_data .= $skin_ins->get_replace_data(
		'work_foot',
		WORK_DATE       => $work_date,
		WORK_DATE_START => $work_date_start,
		WORK_DATE_END   => $work_date_end
	);

	return $skin_data;
}

### エラー表示
sub error {
	my($message) = @_;

	my $skin_ins = new webliberty::Skin;
	$skin_ins->parse_skin($init->{skin_error});

	$skin_ins->replace_skin(
		INFO_ERROR => $message
	);

	print $basis_ins->header;
	print $skin_ins->get_data('_all');

	exit;
}

### 携帯用データ作成
sub get_mobile_data {
	my($data) = @_;

	require Jcode;

	$data =~ s/\xEF\xBD\x9E/\xE3\x80\x9C/g;
	$data = Jcode->new($data, 'utf8')->sjis;

	return($data, length($data) + ($data =~ s/\n/\n/g));
}
