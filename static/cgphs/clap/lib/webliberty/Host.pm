#webliberty::Host.pm (2006/06/18)
#Copyright(C) 2002-2006 Knight, All rights reserved.

package webliberty::Host;

use strict;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
	};
	bless $self, $class;

	return $self;
}

### ホスト取得
sub get_host {
	my $self = shift;

	my $host = $ENV{'REMOTE_HOST'};
	my $addr = $ENV{'REMOTE_ADDR'};

	if (!$host or $host eq $addr) {
		$host = gethostbyaddr(pack('C4', split(/\./, $addr)), 2) or $addr;
	}

	return $host;
}

### IPアドレス取得
sub get_addr {
	my $self = shift;

	return $ENV{'REMOTE_ADDR'};
}

1;
