#webliberty::Basis.pm (2007/02/27)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Basis;

use strict;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
	};
	bless $self, $class;

	return $self;
}

### ヘッダー
sub header {
	my $self = shift;

	return "Content-Type: text/html; charset=utf-8\n\n";
}

### エラー出力
sub error {
	my $self    = shift;
	my $message = shift;

	print $self->header;
	print "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
	print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n";
	print "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"ja\" lang=\"ja\" dir=\"ltr\">\n";
	print "<head>\n";
	print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />\n";
	print "<title>Error</title>\n";
	print "</head>\n";
	print "<body>\n";
	print "<h1>Error</h1>\n";
	print "<ul>\n";
	print "\t<li>$message</li>\n";
	print "</ul>\n";
	print "<address><a href=\"http://www.web-liberty.net/\">Web Liberty</a></address>\n";
	print "</body>\n";
	print "</html>\n";

	exit;
}

### 実行状態記録
sub trace {
	my $self    = shift;
	my $message = shift;
	my $file    = shift;

	if (!$file) {
		$file = './trace.log';
	}

	open(webliberty_Basis, ">>$file") or $self->error("Write Error : $file");
	print webliberty_Basis $message;
	close(webliberty_Basis);

	return;
}

1;
