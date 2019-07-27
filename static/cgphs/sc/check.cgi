#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Web Scheduler : check.cgi - 2015/04/26
#│ copyright (c) KentWeb, 1997-2015
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取込み
require './init.cgi';
my %cf = set_init();

print <<EOM;
Content-type: text/html; charset=utf-8

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
<li>Perlバージョン : $]
EOM

# データファイル
if (-f $cf{numfile}) {
	print "<li>通番ファイルパス : OK\n";
	if (-r $cf{numfile} && -w $cf{numfile}) {
		print "<li>通番ファイルパーミッション : OK\n";
	} else {
		print "<li>通番ファイルパーミッション : NG\n";
	}
} else {
	print "<li>通番ファイルパス : NG\n";
}

# ディレクトリ
my %dir = (
	logdir => 'ログディレクトリ',
	upldir => 'アップディレクトリ',
	);
foreach ( keys %dir ) {
	if (-d $cf{$_}) {
		print "<li>$dir{$_}パス : OK\n";

		if (-r $cf{$_} && -w $cf{$_} && -x $cf{$_}) {
			print "<li>$dir{$_}パーミッション : OK\n";
		} else {
			print "<li>$dir{$_}パーミッション : NG\n";
		}
	} else {
		print "<li>$dir{$_}パス : NG\n";
	}
}

# テンプレート
foreach (qw(list error form)) {
	if (-e "$cf{tmpldir}/$_.html") {
		print "<li>テンプレート( $_.html ) : OK\n";
	} else {
		print "<li>テンプレート( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;

