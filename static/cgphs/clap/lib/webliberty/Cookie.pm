#webliberty::Cookie.pm (2007/06/22)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Cookie;

use strict;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
		id        => shift,
		deskey    => shift,
		cookie    => undef,
		hold_days => undef,
		secure    => undef
	};
	bless $self, $class;

	if ($self->{deskey}) {
		require webliberty::TripleDES;
	}

	$self->{cookie} = $self->_parse_cookie($self->{id});

	return $self;
}

### Cookie取得
sub get_cookie {
	my $self = shift;
	my $info = shift;

	my $cookie;

	if ($info) {
		$cookie = $self->{cookie}->{$info};
	} else {
		$cookie = $self->{cookie};
	}

	return $cookie;
}

### Cookie有効期限設定
sub set_holddays {
	my $self = shift;
	my $info = shift;

	$self->{hold_days} = $info;

	return;
}

### secure属性設定
sub set_secure {
	my $self = shift;
	my $info = shift;

	$self->{secure} = $info;

	return;
}

### Cookie設定
sub set_cookie {
	my $self = shift;
	my %args = @_;

	my %cookie;
	foreach (keys %args) {
		$cookie{$_} = $args{$_};
	}

	my @pairs;
	foreach (sort keys %cookie) {
		$_          =~ s/(\W)/'%' . unpack('H2',$1)/eg;
		$cookie{$_} =~ s/(\W)/'%' . unpack('H2',$1)/eg;

		push(@pairs, $_ . ':' . $cookie{$_});
	}
	my $new_cookie = join('&', @pairs);

	if ($self->{deskey}) {
		my $des_ins = new webliberty::TripleDES($self->{deskey});
		$new_cookie = $des_ins->crypt_string($new_cookie);
	}

	print "Set-Cookie: $self->{id}=$new_cookie;";

	if ($self->{hold_days}) {
		my($sec, $min, $hour, $day, $mon, $year, $wday) = gmtime(time + 60 * 60 * 24 * $self->{hold_days});
		my @week  = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
		my @month = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
		my $date  = sprintf("%s, %02d %s %04d %02d:%02d:%02d GMT", $week[$wday], $day, $month[$mon], $year + 1900, $hour, $min, $sec);

		print " expires=$date";
	}
	if ($self->{secure}) {
		print " secure";
	}

	print "\n";

	return;
}

### Cookie解析
sub _parse_cookie {
	my $self = shift;

	my %all_cookies;
	foreach (split(/; /, $ENV{'HTTP_COOKIE'})) {
		my($key, $value) = split(/=/);
		$all_cookies{$key} = $value;
	}

	if ($self->{deskey} and $all_cookies{$self->{id}} !~ /:/) {
		my $des_ins = new webliberty::TripleDES($self->{deskey});
		$all_cookies{$self->{id}} = $des_ins->encrypt_string($all_cookies{$self->{id}});
	}

	foreach (split(/&/, $all_cookies{$self->{id}})) {
		my($key, $value) = split(/:/);

		$key   =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('C', hex($1))/eg;
		$value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('C', hex($1))/eg;

		$self->{cookie}->{$key} = $value;
	}

	return $self->{cookie};
}

1;
