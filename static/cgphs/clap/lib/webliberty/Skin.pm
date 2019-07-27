#webliberty::Skin.pm (2007/02/27)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Skin;

use strict;
use base qw(webliberty::Basis);

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
		data => undef,
		list => undef
	};
	bless $self, $class;

	return $self;
}

### スキン解析
sub parse_skin {
	my $self = shift;
	my($file, %args) = @_;

	my $available   = $args{'available'};
	my $unavailable = $args{'unavailable'};

	my $skin_info;

	open(webliberty_Skin, $file) or $self->error("Read Error : $file");
	while (<webliberty_Skin>) {
		if (/<!--SKIN_(\w+)_START-->/) {
			$skin_info = lc($1);

			if ($available and $available !~ /(^|\,)$skin_info(\,|$)/) {
				$skin_info = '_unavailable';
			}
			if ($unavailable and $unavailable =~ /(^|\,)$skin_info(\,|$)/) {
				$skin_info = '_unavailable';
			}

			if ($skin_info) {
				push(@{$self->{list}}, $skin_info);
			}
		} elsif (/<!--SKIN_(\w+)_END-->/) {
			$skin_info = '';
		} elsif ($skin_info) {
			$self->{data}->{$skin_info} .= $_;
		} else {
			$self->{data}->{_blank} .= $_;
		}
	}
	close(webliberty_Skin);

	return;
}

### データ置換
sub replace_skin {
	my $self = shift;
	my %args = @_;

	foreach my $data (keys %{$self->{data}}) {
		$self->{data}->{$data} =~ s/\$/\a/g;

		foreach (keys %args) {
			if (/_START$/ or /_END$/) {
				$self->{data}->{$data} =~ s/<!--$_-->/$args{$_}/g;
			} else {
				$self->{data}->{$data} =~ s/\a\{$_\}/$args{$_}/g;
			}
		}

		$self->{data}->{$data} =~ s/\a/\$/g;
	}

	return;
}

### スキンリスト取得
sub get_list {
	my $self = shift;

	return @{$self->{list}};
}

### データ取得
sub get_data {
	my $self = shift;
	my $info = shift;

	if ($info eq '_all') {
		$self->{data}->{_all} .= $self->{data}->{_blank};
	}

	return $self->{data}->{$info};
}

### データ置換取得
sub get_replace_data {
	my $self = shift;
	my($info, %args) = @_;

	if ($info eq '_all') {
		$self->{data}->{_all} .= $self->{data}->{_blank};
	}

	my $skin = $self->{data}->{$info};

	$skin =~ s/\$/\a/g;

	foreach (keys %args) {
		if (/_START$/ or /_END$/) {
			$skin =~ s/<!--$_-->/$args{$_}/g;
		} else {
			$skin =~ s/\a\{$_\}/$args{$_}/g;
		}
	}

	$skin =~ s/\a/\$/g;

	return $skin;
}

1;
