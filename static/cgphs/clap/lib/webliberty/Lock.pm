#webliberty::Lock.pm (2007/02/27)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Lock;

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

### ロック作成
sub file_lock {
	my $self = shift;

	my $flag;

	foreach (1 .. 5) {
		if (-e $self->{file}) {
			if (time > (stat($self->{file}))[9] + 10) {
				$self->file_unlock($self->{file});
				next;
			}
			sleep(1);
		} else {
			if (open(webliberty_Lock, ">$self->{file}")) {
				close(webliberty_Lock);
				$flag = 1;
			}
			last;
		}
	}

	return $flag;
}

### ロック解除
sub file_unlock {
	my $self = shift;

	unlink($self->{file});

	return;
}

1;
