#webliberty::Parser.pm (2007/02/04)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Parser;

use strict;
use base qw(webliberty::Basis);

### コンストラクタ
sub new {
	my $class = shift;
	my %args  = @_;

	my $self = {
		max   => $args{'max'},
		jcode => $args{'jcode'},
		plain => $args{'plain'},
		query => undef,
		list  => undef,
		file  => undef
	};
	bless $self, $class;

	if (!$self->{max}) {
		$self->{max} = 15000;
	}
	if ($self->{jcode}) {
		require Jcode;
	}
	if ($ENV{'CONTENT_LENGTH'} or $ENV{'QUERY_STRING'}) {
		$self->{query} = $self->_parse_query($self->{max});
	}

	return $self;
}

### データ取得
sub get_query {
	my $self = shift;
	my $name = shift;

	my $query;

	if ($name) {
		$query = $self->{query}->{$name};
	} else {
		$query = $self->{query};
	}

	return $query;
}

### ファイル名取得
sub get_filename {
	my $self = shift;
	my $name = shift;

	my $filename;

	if ($self->{query}->{$name}) {
		$filename = $self->{query}->{$name}->{file_name};
	}

	return $filename;
}

### ファイルデータ取得
sub get_filedata {
	my $self = shift;
	my $name = shift;

	my $filedata;

	if ($self->{query}->{$name}) {
		$filedata = $self->{query}->{$name}->{file_data};
	}

	return $filedata;
}

### ファイルサイズ取得
sub get_filesize {
	my $self = shift;
	my $name = shift;

	my $filesize;

	if ($self->{query}->{$name}) {
		$filesize = $self->{query}->{$name}->{file_size};
	}

	return $filesize;
}

### マイムタイプ取得
sub get_mimetype {
	my $self = shift;
	my $name = shift;

	my $mimetype;

	if ($self->{query}->{$name}) {
		$mimetype = $self->{query}->{$name}->{mime_type};
	}

	return $mimetype;
}

### データ一覧取得
sub get_datalist {
	my $self = shift;

	my @list;

	if ($self->{list}) {
		@list = @{$self->{list}};
	}

	return @list;
}

### ファイル一覧取得
sub get_filelist {
	my $self = shift;

	my @list;

	if ($self->{file}) {
		@list = @{$self->{file}};
	}

	return @list;
}

### データ解析
sub _parse_query {
	my $self = shift;

	my($alldata, $query);

	if ($ENV{'CONTENT_TYPE'} =~ /^multipart\/form-data;\s+boundary=(.+)/) {
		my $boundary = $1;

		binmode(STDIN);
		read(STDIN, $alldata, $ENV{'CONTENT_LENGTH'});

		my($key, $file);

		foreach (split(/\r\n/, $alldata)) {
			if (/$boundary/) {
				if ($file->{file_name}) {
					$query->{$key} = $file;
					$file = undef;
				}
			} else {
				if (/^Content-Disposition:\sform-data;\sname=\"([^\"]*)\"/) {
					$key = $1;
					if (/filename=\"([^\"]*)\"/i) {
						$file->{file_name} = $1;
					}
				} elsif (/^Content-Type:\s(\S+)/) {
					$file->{mime_type} = $1;
				} else {
					if ($file->{file_name}) {
						if ($file->{file_data}) {
							$file->{file_data} .= "\r\n";
						} elsif (!exists($file->{file_data})) {
							push(@{$self->{list}}, $key);
							push(@{$self->{file}}, $key);
						}
						$file->{file_data} .= $_;

						$file->{file_size} += length("$_\r\n");
					} else {
						if ($query->{$key}) {
							$query->{$key} .= "\n";
						} elsif (!exists($query->{$key})) {
							push(@{$self->{list}}, $key);
						}
						$query->{$key} .= $self->_create_text($_);
					}
				}
			}
		}
	} else {
		if ($ENV{'REQUEST_METHOD'} eq 'POST') {
			if ($self->{max} and $ENV{'CONTENT_LENGTH'} > $self->{max}) {
				$self->error("最大受信容量は$self->{max}byteです。（現在$ENV{'CONTENT_LENGTH'}byte。）");
			} else {
				read(STDIN, $alldata, $ENV{'CONTENT_LENGTH'});
			}
		} else {
			$alldata = $ENV{'QUERY_STRING'};
		}
		foreach (split(/&/, $alldata)) {
			my($key, $value) = split(/=/);

			$key   =~ tr/+/ /;
			$key   =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;

			$value =~ tr/+/ /;
			$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;

			$value = $self->_create_text($value);

			if ($query->{$key}) {
				$query->{$key} .= "\n";
			} elsif (!exists($query->{$key})) {
				push(@{$self->{list}}, $key);
			}
			$query->{$key} .= $value;
		}
	}

	return $query;
}

### テキストデータ作成
sub _create_text {
	my $self = shift;
	my $text = shift;

	if ($self->{jcode} and $text =~ /[^\w\.\~\-\/\?\&\#\+\=\:\;\@\%]+/) {
		my $code = Jcode->getcode($text);

		if ($code ne 'ascii' and $code ne 'utf8' and $code ne '') {
			$text =~ s/\xEF\xBD\x9E/\xE3\x80\x9C/g;
			$text = Jcode->new($text)->utf8;
		}
	}
	if (!$self->{plain}) {
		$text =~ s/&/&amp;/g;
		$text =~ s/</&lt;/g;
		$text =~ s/>/&gt;/g;
		$text =~ s/"/&quot;/g;
	}

	return $text;
}

1;
