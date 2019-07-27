package init;

#Web Clap Ver 2.09：設定ファイル
#
#Copyright(C) 2002-2007 Knight, All rights reserved.
#Mail ... support@web-liberty.net
#Home ... http://www.web-liberty.net/

use strict;

sub get_init {
	my $init;

	#――――― 基本設定 ―――――――――――――――――――

	#管理者ページタイトル
	$init->{admin_title} = '拍手管理';

	#管理者パスワード
	$init->{admin_pwd} = 'trrm5492';

	#ログを保存する日数
	$init->{save_days} = 365;

	#ログ保存日数を超えたファイル(0 … 完全に削除 / 1 … メッセージのみ残す)
	$init->{save_message} = 1;

	#連続拍手最大送信数(0にすると無制限)
	$init->{limit_count} = 10;

	#連続拍手とみなす時間(分で指定)
	$init->{limit_interval} = 1440;

	#お礼画面の表示方法(0 … ランダムに表示 / 1 … 順番に表示)
	$init->{order_mode} = 0;

	#送信メッセージの事後確認(0 … 表示しない / 1 … 送信済みメッセージを確認表示)
	$init->{confirm_mode} = 1;

	#拍手を受け付けないホスト
	@{$init->{refuse_host}} = (
		'',
		'',
		'',
		'',
		''
	);

	#――――― 総拍手数記録の設定 ――――――――――――――

	#総拍手数の記録(0 … 記録しない / 1 … 記録する)
	$init->{count_mode} = 1;

	#総拍手数記録ファイル
	$init->{count_file} = './count.log';

	#――――― お礼画面強制表示の設定 ――――――――――――

	#特定のお礼画面を強制表示した後の、2回目以降のお礼画面(0 … 普通に表示 / 1 … 1回目と同じ画面を表示)
	$init->{second_mode} = 0;

	#――――― お礼登録画面の設定 ――――――――――――――

	#IDの指定(0 … 指定不可 / 1 … 指定可能)
	$init->{use_id} = 0;

	#公開設定(0 … 指定不可 / 1 … 指定可能)
	$init->{use_stat} = 0;

	#表示対象設定(0 … 指定不可 / 1 … 指定可能)
	$init->{use_target} = 0;

	#説明の入力(0 … 指定不可 / 1 … 指定可能)
	$init->{use_explain} = 0;

	#ファイルアップロード(0 … アップロード不可 / 1 … アップロード可能)
	$init->{use_file} = 1;

	#PC用送信完了画面スキンの指定(0 … 指定不可 / 1 … 指定可能)
	$init->{use_skin_pc} = 1;

	#携帯用送信完了画面スキンの指定(0 … 指定不可 / 1 … 指定可能)
	$init->{use_skin_mobile} = 1;

	#――――― 送信済み拍手閲覧画面の設定 ――――――――――

	#拍手一覧画面での、拍手が無い時間のセルの表示(0 … 表示しない / 1 … 表示する)
	$init->{show_void} = 0;

	#送信元ページごとの拍手数集計(0 … 表示しない / 1 … 表示する)
	$init->{page_mode} = 1;

	#メッセージ一覧画面での、１ページの表示件数
	$init->{message_size} = 20;

	#ホスト情報の表示(0 … 表示しない / 1 … 表示する)
	$init->{show_host} = 1;

	#――――― グラフの設定 ―――――――――――――――――

	#拍手一覧表示グラフの縮小率
	$init->{cutdown_list} = 0.1;

	#日時別一覧表示グラフの縮小率
	$init->{cutdown_date} = 0.1;

	#送信元ページ別一覧グラフの縮小率
	$init->{cutdown_page} = 0.5;

	#――――― 入力制限の設定 ――――――――――――――――

	#メッセージの最大文字数
	$init->{max_message} = 1000;

	#投稿禁止ワード
	@{$init->{ng_word}} = (
		'',
		'',
		'',
		'',
		''
	);

	#日本語の利用(0 … 任意 / 1 … 必須)
	$init->{need_japanese} = 0;

	#記述できるURLの最大数(0にすると無制限)
	$init->{max_link} = 0;

	#メッセージ欄以外へのURLの記述(0 … 禁止しない / 1 … 禁止する)
	$init->{other_link} = 0;

	#不正なデータ受信時の動作(0 … 受信完了画面を表示 / 1 … エラー画面を表示)
	$init->{error_mode} = 1;

	#――――― メール送信の設定 ―――――――――――――――

	#メッセージ通知機能の利用(0 … 使用しない / 1 … 使用する)
	$init->{sendmail_mode} = 1;

	#送信先メールアドレス
	@{$init->{sendmail_list}} = (
		'eizi2002sabu@gmail.com',
		'',
		'',
		'',
		''
	);

	#送信メールの件名
	$init->{sendmail_subject} = 'メインサイトのweb拍手にメッセージが投稿されました';

	#sendmailのパス
	$init->{sendmail_path} = '/usr/sbin/sendmail';

	#――――― システムの設定 ――――――――――――――――

	#受信データの文字コード変換(0 … 変換しない / 1 … 変換する)
	$init->{jcode_mode} = 0;

	#送信完了画面スキン
	$init->{skin_thanks} = './skin/thanks.html';

	#送信完了画面スキン格納ディレクトリ
	$init->{skin_thanks_dir} = './skin/thanks_pc/';

	#最大連続拍手数を超えた場合のスキン
	$init->{skin_limit} = './skin/limit.html';

	#エラー画面スキン
	$init->{skin_error} = './skin/error.html';

	#携帯用ページスキン - 送信完了画面スキン
	$init->{skin_mobile_thanks} = './skin/mobile_thanks.html';

	#携帯用ページスキン - 送信完了画面スキン格納ディレクトリ
	$init->{skin_mobile_thanks_dir} = './skin/thanks_mobile/';

	#携帯用ページスキン - 最大連続拍手数を超えた場合のスキン
	$init->{skin_mobile_limit} = './skin/mobile_limit.html';

	#携帯用ページスキン - エラー画面スキン
	$init->{skin_mobile_error} = './skin/mobile_error.html';

	#管理者ページスキン - ログイン画面
	$init->{skin_login} = './skin/login.html';

	#管理者ページスキン - ヘッダー
	$init->{skin_admin_header} = './skin/admin_header.html';

	#管理者ページスキン - フッター
	$init->{skin_admin_footer} = './skin/admin_footer.html';

	#管理者ページスキン - 拍手一覧
	$init->{skin_admin_list} = './skin/admin_list.html';

	#管理者ページスキン - 日時別一覧
	$init->{skin_admin_date} = './skin/admin_date.html';

	#管理者ページスキン - 送信元ページ別一覧
	$init->{skin_admin_page} = './skin/admin_page.html';

	#管理者ページスキン - メッセージ一覧
	$init->{skin_admin_message} = './skin/admin_message.html';

	#管理者ページスキン - お礼登録画面
	$init->{skin_admin_form} = './skin/admin_form.html';

	#管理者ページスキン - お礼画面一覧
	$init->{skin_admin_edit} = './skin/admin_edit.html';

	#スキンファイルの拡張子
	$init->{skin_exit} = 'html';

	#管理者プログラム
	$init->{script_file} = './admin.cgi';

	#ログ保存ディレクトリ
	$init->{logs_dir} = './logs/';

	#過去メッセージ保存ディレクトリ
	$init->{past_dir} = './past/';

	#ログファイルの拡張子
	$init->{logs_ext} = 'log';

	#お礼画面ログファイル
	$init->{thanks_file} = './thanks.log';

	#アップロードファイル保存ディレクトリ
	$init->{upfile_dir} = './upfile/';

	#ロックファイル
	$init->{lock_file} = './lock/clap.lock';

	#――――― Cookieの設定 ―――――――――――――――――

	#Cookieの識別名
	$init->{cookie_admin} = 'webclap';

	#トリプルDES暗号キー
	$init->{des_key} = '';

	return $init;
}

1;
