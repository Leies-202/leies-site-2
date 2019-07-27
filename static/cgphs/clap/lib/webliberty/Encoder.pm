#webliberty::Encoder.pm (2006/02/18)
#Copyright(C) 2002-2006 Knight, All rights reserved.

package webliberty::Encoder;

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

### URLエンコード
sub url_encode {
	my $self = shift;

	$self->{string} =~ s/(\W)/'%' . unpack('H2', $1)/eg;

	return $self->{string};
}

### BASE64エンコード(参考：http://www.tohoho-web.com/)
sub base64_encode {
	my $self = shift;

	my $base = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
	my($xx, $yy, $zz, $i);

	$xx = unpack('B*', $self->{string});

	for ($i = 0; $yy = substr($xx, $i, 6); $i += 6) {
		$zz .= substr($base, ord(pack('B*', '00' . $yy)), 1);

		if (length($yy) == 2) {
			$zz .= '==';
		} elsif (length($yy) == 4) {
			$zz .= '=';
		}
	}

	$self->{string} = $zz;

	return $self->{string};
}

### データ取得
sub get_string {
	my $self = shift;

	return $self->{string};
}

1;
