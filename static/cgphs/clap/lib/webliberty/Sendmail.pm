#webliberty::Sendmail.pm (2007/02/27)
#Copyright(C) 2002-2007 Knight, All rights reserved.

package webliberty::Sendmail;

use strict;
use Jcode;
use webliberty::Encoder;

### コンストラクタ
sub new {
	my $class = shift;

	my $self = {
		sendmail  => shift,
		send_to   => undef,
		send_from => undef,
		subject   => undef,
		name      => undef,
		message   => undef,
		files     => undef,
		x_mailer  => undef
	};
	bless $self, $class;

	return $self;
}

### メール送信
sub sendmail {
	my $self = shift;
	my %args = @_;

	$self->{send_to}   = $args{'send_to'};
	$self->{send_from} = $args{'send_from'};
	$self->{subject}   = $args{'subject'};
	$self->{name}      = $args{'name'};
	$self->{message}   = $args{'message'};
	$self->{files}     = $args{'files'};
	$self->{x_mailer}  = $args{'x_mailer'};

	if (!$self->{send_to}) {
		$self->{send_to} = 'example@example.com';
	}
	if (!$self->{send_from}) {
		$self->{send_from} = 'example@example.com';
	}
	if (!$self->{subject}) {
		$self->{subject} = 'No Subject';
	}
	if (!$self->{message}) {
		$self->{message} = 'No Message';
	}
	if (!$self->{x_mailer}) {
		$self->{x_mailer} = 'Web Liberty';
	}

	foreach ($self->{subject}, $self->{name}, $self->{message}) {
		$_ =~ s/<br \/>/\n/g;
		$_ =~ s/&amp;/&/g;
		$_ =~ s/&lt;/</g;
		$_ =~ s/&gt;/>/g;
		$_ =~ s/&quot;/"/g;
	}

	if ($self->{name}) {
		$self->{send_from} = "\"" . $self->_encode($self->{name}) . "\" <$self->{send_from}>";
	}

	$self->{message} =~ s/\xEF\xBD\x9E/\xE3\x80\x9C/g;
	$self->{message} = Jcode->new($self->{message}, 'utf8')->jis;

	my @files = split(/\n/, $args{'files'});

	my $boundary;
	if ($files[0]) {
		require webliberty::File;

		$boundary = time;
		while ($self->{message} =~ /$boundary/) {
			$boundary++;
		}
	}

	open(webliberty_Sendmail, "| $self->{sendmail} -t") or return(0, "Sendmail Error : $self->{sendmail}");
	print webliberty_Sendmail "X-Mailer: $self->{x_mailer}\n";
	print webliberty_Sendmail "To: $self->{send_to}\n";
	print webliberty_Sendmail "From: $self->{send_from}\n";
	print webliberty_Sendmail "Subject: " . $self->_encode($self->{subject}) . "\n";

	if ($files[0]) {
		print webliberty_Sendmail "Content-Type: multipart/mixed; boundary=\"$boundary\"\n\n";
		print webliberty_Sendmail "--$boundary\n";
	}

	print webliberty_Sendmail "Content-Transfer-Encoding: 7bit\n";
	print webliberty_Sendmail "Content-Type: text/plain; charset=iso-2022-jp\n\n";
	print webliberty_Sendmail "$self->{message}\n";

	foreach (@files) {
		my $file_ins = new webliberty::File($_);
		my $file_name = $file_ins->get_name . '.' . $file_ins->get_ext;

		print webliberty_Sendmail "--$boundary\n";
		print webliberty_Sendmail "Content-Type: application/octet-stream; name=\"$file_name\"\n";
		print webliberty_Sendmail "Content-Transfer-Encoding: X-uuencode\n";
		print webliberty_Sendmail "Content-Disposition: attachment; filename=\"$file_name\"\n\n";

		if (open(webliberty_Sendmail_FILE, $_)) {
			binmode(webliberty_Sendmail_FILE);
			print webliberty_Sendmail $self->_uuencode(join('', <webliberty_Sendmail_FILE>), $file_name);
			close(webliberty_Sendmail_FILE);
		}
	}

	close(webliberty_Sendmail);

	return 1;
}

### テキストエンコード
sub _encode {
	my $self = shift;
	my $text = shift;

	$text =~ s/\xEF\xBD\x9E/\xE3\x80\x9C/g;
	$text = Jcode->new($text, 'utf8')->jis;
	$text =~ s/\x1b\x28\x42/\x1b\x28\x4a/g;

	my $string_ins = new webliberty::Encoder($text);
	$string_ins->base64_encode;

	$text = '=?iso-2022-jp?B?' . $string_ins->get_string . '?=';

	return $text;
}

### ファイルエンコード
sub _uuencode {
	my $self = shift;
	my $data = shift;
	my $name = shift;

	my $result;
	while ($data =~ s/^((.|\n){45})//) {
		$result .= pack('u', $&);
	}
	if ($data ne '') {
		$result .= pack('u', $data);
	}
	$result =~ s/`/ /g;
	$result = "begin 644 $name\n$result \nend\n";

	return $result;
}

1;
