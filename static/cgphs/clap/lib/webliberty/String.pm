#webliberty::String.pm (2007/06/22)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::String;

use strict;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
		string => shift
	};
	bless $self, $class;

	return $self;
}

### 一行データ作成
sub create_line {
	my $self = shift;

	$self->{string} =~ s/^\s+//;
	$self->{string} =~ s/\s+$//;
	$self->{string} =~ s/\t//g;
	$self->{string} =~ s/\r//g;
	$self->{string} =~ s/\n//g;
	$self->{string} =~ s/<br \/>//g;

	return $self->{string};
}

### 複数行データ作成
sub create_text {
	my $self = shift;

	$self->{string} =~ s/\t//g;
	$self->{string} =~ s/\r?\n/\r/g;
	$self->{string} =~ s/^\r+//;
	$self->{string} =~ s/\r+$//;
	$self->{string} =~ s/\r/<br \/>/g;

	return $self->{string};
}

### 数値データ作成
sub create_number {
	my $self = shift;

	$self->{string} = int($self->{string});

	return $self->{string};
}

### プレーンデータ作成
sub create_plain {
	my $self = shift;

	$self->{string} =~ s/\r?\n/\n/g;
	$self->{string} =~ s/<br \/>/\n/g;

	return $self->{string};
}

### リンク作成
sub create_link {
	my $self      = shift;
	my $attribute = shift;

	if ($attribute) {
		$attribute = " $attribute";
		$attribute =~ s/&quot;/"/g;
	}

	$self->{string} = "\n$self->{string}\n";
	$self->{string} =~ s/([^\"(&quot;)(&gt;)])(https?:\/\/[\w\.\~\-\/\?\&\#\+\=\:\;\@\%]+)([^\"(&quot;)(&lt;)])/$1<a href="$2"$attribute>$2<\/a>$3/gi;
	$self->{string} =~ s/([^\"(&quot;)(&gt;)])(ftp:\/\/[\w\.\~\-\/\?\&\#\+\=\:\;\@\%]+)([^\"(&quot;)(&lt;)])/$1<a href="$2"$attribute>$2<\/a>$3/gi;
	$self->{string} =~ s/([^\"(&quot;)(&gt;)])([\w\-]+\@[\w\-\.]+)([^\"(&quot;)(&lt;)])/$1<a href="mailto:$2">$2<\/a>$3/gi;
	$self->{string} =~ s/^\n//;
	$self->{string} =~ s/\n$//;

	return $self->{string};
}

### パスワード作成
sub create_password {
	my $self = shift;

	my $salt = pack('CC', int(rand(26) + 65), int(rand(10) + 48));
	$self->{string} = crypt($self->{string}, $salt);

	return $self->{string};
}

### HTML有効化
sub permit_html {
	my $self = shift;

	$self->{string} =~ s/&quot;/"/g;
	$self->{string} =~ s/&lt;/</g;
	$self->{string} =~ s/&gt;/>/g;
	$self->{string} =~ s/&amp;/&/g;

	return $self->{string};
}

### 文字数取得
sub check_length {
	my $self = shift;

	return length($self->{string});
}

### 行数取得
sub check_line {
	my $self = shift;

	return ($self->{string} =~ s/<br \/>/<br \/>/g) + 1;
}

### 指定文字列数取得
sub check_count {
	my $self   = shift;
	my $string = shift;

	return ($self->{string} =~ s/$string/$string/g);
}

### パスワード照合
sub check_password {
	my $self     = shift;
	my $password = shift;

	my $flag;

	if ($self->{string} and $password and crypt($self->{string}, $password) eq $password) {
		$flag = 1;
	}

	return $flag;
}

### データ設定
sub set_string {
	my $self   = shift;
	my $string = shift;

	$self->{string} = $string;

	return;
}

### データ置換
sub replace_string {
	my $self   = shift;
	my $before = shift;
	my $after  = shift;

	$self->{string} =~ s/$before/$after/g;

	return $self->{string};
}

### データ省略
sub trim_string {
	my $self   = shift;
	my $width  = shift;
	my $marker = shift;

	if (length($self->{string}) > $width) {
		$self->{string} = substr($self->{string}, 0, $width);

		if ($self->{string} !~ /[\x00-\x7F]$/) {
			$self->{string} =~ s/[\xC0-\xFD]$//;
			$self->{string} =~ s/[\xE0-\xFD][\x80-\xBF]$//;
			$self->{string} =~ s/[\xF0-\xFD][\x80-\xBF]{2}$//;
		}

		$self->{string} .= $marker;
	}

	return $self->{string};
}

### データ取得
sub get_string {
	my $self = shift;

	return $self->{string};
}

1;
