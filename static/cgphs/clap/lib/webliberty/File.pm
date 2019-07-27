#webliberty::File.pm (2007/02/27)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::File;

use strict;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
		file => shift
	};
	bless $self, $class;

	return $self;
}

### ファイル名取得
sub get_name {
	my $self = shift;

	$self->{file} =~ /([^\/\\]*)\.[^.\/\\]*$/;

	return lc($1);
}

### ファイル拡張子取得
sub get_ext {
	my $self = shift;

	$self->{file} =~ /[^\/\\]*\.([^.\/\\]*)$/;

	return lc($1);
}

### ファイルサイズ取得
sub get_size {
	my $self = shift;

	my($width, $height);
	my $ext = $self->get_ext;

	open(webliberty_File, $self->{file}) or return(0, 0);
	binmode(webliberty_File);
	if ($ext eq 'gif') {
		($width, $height) = $self->_get_gifsize(*webliberty_File);
	} elsif ($ext eq 'jpeg' or $ext eq 'jpg' or $ext eq 'jpe') {
		($width, $height) = $self->_get_jpegsize(*webliberty_File);
	} elsif ($ext eq 'png') {
		($width, $height) = $self->_get_pngsize(*webliberty_File);
	}
	close(webliberty_File);

	return($width, $height);
}

### ファイル複製
sub copy {
	my $self = shift;
	my $file = shift;

	open(webliberty_File_ORG, "$self->{file}") or return 0;
	binmode(webliberty_File_ORG);

	open(webliberty_File_COPY, ">$file") or return 0;
	binmode(webliberty_File_COPY);
	print webliberty_File_COPY <webliberty_File_ORG>;
	close(webliberty_File_COPY);

	close(webliberty_File_ORG);

	return 1;
}

### GIFサイズ取得(参考：http://www.bloodyeck.com/wwwis/)
sub _get_gifsize {
	my $self = shift;
	my($GIF) = @_;

	my($type, $a, $b, $c, $d, $s) = 0;

	if (defined($GIF) and read($GIF, $type, 6) and $type =~ /GIF8[7,9]a/ and read($GIF, $s, 4) == 4) {
		($a, $b, $c, $d) = unpack("C"x4, $s);
		return ($b << 8 | $a, $d << 8 | $c);
	}

	return(0, 0);
}

### JPEGサイズ取得(参考：http://www.bloodyeck.com/wwwis/)
sub _get_jpegsize {
	my $self  = shift;
	my($JPEG) = @_;

	my($done, $c1, $c2, $ch, $s, $length, $dummy) = 0;
	my($a, $b, $c, $d);

	if (defined($JPEG) and read($JPEG, $c1, 1) and read($JPEG, $c2, 1) and ord($c1) == 0xFF and ord($c2) == 0xD8) {
		while (ord($ch) != 0xDA and !$done) {
			while (ord($ch) != 0xFF) {
				return(0, 0) unless read($JPEG, $ch, 1);
			}
			while (ord($ch) == 0xFF) {
				return(0, 0) unless read($JPEG, $ch, 1);
			}
			if ((ord($ch) >= 0xC0) and (ord($ch) <= 0xC3)) {
				return(0, 0) unless read($JPEG, $dummy, 3);
				return(0, 0) unless read($JPEG, $s, 4);
				($a, $b, $c, $d) = unpack("C"x4, $s);
				return ($c << 8 | $d, $a << 8 | $b);
			} else {
				return(0, 0) unless read ($JPEG, $s, 2);
				($c1, $c2) = unpack("C"x2, $s);
				$length = $c1 << 8 | $c2;
				last if (!defined($length) or $length < 2);
				read($JPEG, $dummy, $length - 2);
			}
		}
	}

	return(0, 0);
}

### PNGサイズ取得(参考：http://www.bloodyeck.com/wwwis/)
sub _get_pngsize {
	my $self = shift;
	my($PNG) = @_;

	my $head;
	my($a, $b, $c, $d, $e, $f, $g, $h) = 0;

	if (defined($PNG) and read($PNG, $head, 8) == 8 and $head eq "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" and read($PNG, $head, 4) == 4 and read($PNG, $head, 4) == 4 and $head eq "IHDR" and read($PNG, $head, 8) == 8){
		($a, $b, $c, $d, $e, $f, $g, $h) = unpack("C"x8, $head);
		return ($a << 24 | $b << 16 | $c << 8 | $d, $e << 24 | $f << 16 | $g << 8 | $h);
	}

	return(0, 0);
}

1;
