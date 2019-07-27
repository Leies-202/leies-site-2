#┌─────────────────────────────────
#│ 祝日ライブラリ holiday v3.0
#│ holiday.pl - 2014/09/23
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────
# 【留意事項・免責事項】
#  ＊文字コードは「シフトJIS」で記述しています。必要に応じてエディタ等
#    でコード変換を行ってください。
#
# 【利用の仕方】
#  (1) 祝日チェック[特定日] (戻り値: 祝日の名称）
#      $holiday = &holiday::holiday($yyyy, $mm, $dd);
#
#  (2) 祝日チェック[月単位の祝日] (戻り値: 祝日=祝日の名称 祝日以外=0）
#      %holiday = &holiday::holi_mon($yyyy, $mm);
#
#  (3) 曜日取得 (戻り値: 0=日 1=月 ... 6=土）
#      $week = &holiday::get_week($yyyy, $mm, $dd);
#
#  (4) 月の「末日」
#      $last_day = &holiday::last_day($yyyy, $mm);

package holiday;

#-----------------------------------------------------------
#  定義
#-----------------------------------------------------------
sub set_conf {
	my $year = shift;
	my $v_day = vernal_equinox($year);
	my $a_day = autumnal_equinox($year);
	
	# 固定日付 → mm-dd形式
	my %holiday = (
		'01-01' => '元日',
		'02-11' => '建国記念の日',
		'04-29' => '昭和の日',
		'05-04' => 'みどりの日',
		'05-03' => '憲法記念日',
		'05-05' => 'こどもの日',
		'08-11' => '山の日', # 2016年以降
		'11-03' => '文化の日',
		'11-23' => '勤労感謝の日',
		'12-23' => '天皇誕生日',
	);
	# 春・秋分の日
	$holiday{"03-$v_day"} = '春分の日';
	$holiday{"09-$a_day"} = '秋分の日';
	
	# ハッピーマンデー → mm月の第何週
	my %happy = (
		'01-2' => '成人の日',
		'07-3' => '海の日',
		'09-3' => '敬老の日',
		'10-2' => '体育の日',
	);
	
	# その他
	my %others = (
		furi => '振替休日',
		koku => '国民の休日',
	);
	# --- 基本定義ここまで
	
	if ($year < 2016) { delete($holiday{'08-11'}); }
	return (\%holiday,\%happy,\%others);
}

#-----------------------------------------------------------
#  祝日チェック（特定日）
#-----------------------------------------------------------
sub holiday {
	my ($y,$m,$d) = @_;
	$m = sprintf("%02d",$m);
	$d = sprintf("%02d",$d);
	
	# 定義
	my ($hol,$hap,$oth) = set_conf($y);

	# 照合
	if (defined($$hol{"$m-$d"})) { return $$hol{"$m-$d"};	}

	# 月曜日ならば振替休日をチェックする
	if (get_week($y,$m,$d) == 1) {

		# ハッピーマンデー照合
		my $hit = happy_monday($m,$d,$hap);
		if ($hit) { return $hit; }

		# 前日を求める
		my ($mday,$mon,$year,$wday) = get_day($y,$m,$d,-1);

		# 前日が祝日ならば振替休日
		if (defined($$hol{"$mon-$mday"})) { return $$oth{furi}; }
	}
	# 2007以後、5/3,4が日曜のとき → 5/6が振替
	if ($y >= 2007 && $m == 5 && $d == 6) {
		if (get_week($y,5,3) == 0 || get_week($y,5,4) == 0) { return $$oth{furi}; }
	}

	# 国民の休日 → 敬老の日と秋分の日に挟まれた祝日
	if ($y >= 2003 && $m == 9) {

		# 前日が第3月曜日（敬老の日）か
		my ($mday,$mon,$year,$wday) = get_day($y,$m,$d,-1);
		my $mshu = int( ($mday - 1) / 7 ) + 1;

		# 翌日が秋分の日か
		my ($mday2,$mon2,$year2,$wday2) = get_day($y,$m,$d,+1);

		if ($mshu == 3 && $wday == 1 && autumnal_equinox($year2) == $mday2) {
			return $$oth{koku};
		}
	}
	return 0;
}

#-----------------------------------------------------------
#  祝日チェック（月単位）
#-----------------------------------------------------------
sub holi_mon {
	my ($y,$m) = @_;
	$m = sprintf("%02d",$m);
	
	# 定義
	my ($hol,$hap,$oth) = set_conf($y);
	
	my $w = get_week($y,$m,1);
	my $last = last_day($y,$m);
	my %day;
	foreach my $i (1 .. $last) {
		$i = sprintf("%02d",$i);

		# 固定
		if (defined($$hol{"$m-$i"})) {
			$day{$i} = $$hol{"$m-$i"};

		# 月曜のとき
		} elsif ($w == 1) {
			# ハッピーマンデー照合
			my $hit = happy_monday($m,$i,$hap);
			if ($hit) { $day{$i} = $hit; }

			# 前日を求める
			my ($mday,$mon,$year,$wday) = get_day($y,$m,$i,-1);

			# 前日が祝日ならば振替休日
			if (defined($$hol{"$mon-$mday"})) { $day{$i} = $$oth{furi}; }

		# 2007以後、5/3,4が日曜のとき → 5/6が振替
		} elsif ($y >= 2007 && $m == 5 && $i == 6) {
			if (get_week($y,5,3) == 0 || get_week($y,5,4) == 0) {
				$day{$i} = $$oth{furi};
			}

		# 国民の休日　→　敬老の日と秋分の日に挟まれた祝日
		} elsif ($y >= 2003 && $m == 9) {
			# 前日が第3月曜日（敬老の日）か
			my ($mday,$mon,$year,$wday) = get_day($y,$m,$i,-1);
			my $mshu = int( ($mday - 1) / 7 ) + 1;

			# 翌日が秋分の日か
			my ($mday2,$mon2,$year2,$wday2) = get_day($y,$m,$i,+1);

			if ($mshu == 3 && $wday == 1 && autumnal_equinox($year2) == $mday2) {
				$day{$i} = $$oth{koku};
			}
		}

		# 週
		$w = $w >= 6 ? 0 : ++$w;
	}
	return %day;
}

#-----------------------------------------------------------
#  ハッピーマンデー確認
#-----------------------------------------------------------
sub happy_monday {
	my ($mm,$dd,$happy) = @_;

	# 月の第何週か
	my $mshu = int( ($dd - 1) / 7 ) + 1;

	# ハッピーマンデー照合
	my $hit;
	while ( my ($key,$val) = each %{$happy} ) {
		my ($mon,$shu) = split(/-/,$key);

		if ($mm == $mon && $mshu == $shu) {
			$hit = $val;
			last;
		}
	}
	return $hit;
}

#-----------------------------------------------------------
#  週算出
#-----------------------------------------------------------
sub get_week {
	my ($yy,$mm,$dd) = @_;

	if ($mm == 1 || $mm == 2) {
		$yy--;
		$mm += 12;
	}
	int( $yy + int($yy / 4) - int($yy / 100) + int($yy / 400) + int((13 * $mm + 8) / 5) + $dd ) % 7;
}

#-----------------------------------------------------------
#  特定日算出
#-----------------------------------------------------------
sub get_day {
	my ($yy,$mm,$dd,$key) = @_;

	# 特定時間を算出
	my $time = timelocal(0,0,12,$dd,$mm-1,$yy-1900) + (24 * 60 * 60 * $key);

	# 年月日週を算出
	my ($mday,$mon,$year,$wday) = (localtime($time))[3..6];
	$mday = sprintf("%02d",$mday);
	$mon  = sprintf("%02d",$mon+1);
	$year += 1900;
	return ($mday,$mon,$year,$wday);
}

#-----------------------------------------------------------
#  春分の日
#-----------------------------------------------------------
sub vernal_equinox {
	my $yy = shift;

	my $dd;
	if ($yy < 2099) {
		$dd = int( 20.8431 + 0.242194 * ($yy - 1980) - int(($yy - 1980) / 4) );
	} elsif ($yy < 2155) {
		$dd = int( 21.8510 + 0.242194 * ($yy - 1980) - int(($yy - 1980) / 4) );
	}
	sprintf("%02d",$dd);
}

#-----------------------------------------------------------
#  秋分の日
#-----------------------------------------------------------
sub autumnal_equinox {
	my $yy = shift;

	my $dd;
	if ($yy < 2099) {
		$dd = int( 23.2488 + 0.242194 * ($yy - 1980) - int(($yy - 1980) / 4) );
	} elsif ($yy < 2155) {
		$dd = int( 24.2488 + 0.242194 * ($yy - 1980) - int(($yy - 1980) / 4) );
	}
	sprintf("%02d",$dd);
}

#-----------------------------------------------------------
#  月の末日
#-----------------------------------------------------------
sub last_day {
	my ($yy, $mm) = @_;

	return (31,28,31,30,31,30,31,31,30,31,30,31) [$mm - 1]
	+ ($mm == 2 && (($yy % 4 == 0 && $yy % 100 != 0) || $yy % 400 == 0));
}

#-----------------------------------------------------------
#  標準ライブラリ (timelocal.pl) 引用
#-----------------------------------------------------------
CONFIG: {
    local($[) = 0;
    @epoch = localtime(0);
    $tzmin = $epoch[2] * 60 + $epoch[1];	# minutes east of GMT
    if ($tzmin > 0) {
	$tzmin = 24 * 60 - $tzmin;		# minutes west of GMT
	$tzmin -= 24 * 60 if $epoch[5] == 70;	# account for the date line
    }

    $SEC = 1;
    $MIN = 60 * $SEC;
    $HR = 60 * $MIN;
    $DAYS = 24 * $HR;
    $YearFix = ((gmtime(946684800))[5] == 100) ? 100 : 0;
    1;
}
sub timegm {
    local($[) = 0;
    $ym = pack(C2, @_[5,4]);
    $cheat = $cheat{$ym} || &cheat;
    return -1 if $cheat<0;
    $cheat + $_[0] * $SEC + $_[1] * $MIN + $_[2] * $HR + ($_[3]-1) * $DAYS;
}
sub timelocal {
    local($[) = 0;
    $time = &timegm + $tzmin*$MIN;
    return -1 if $cheat<0;
    @test = localtime($time);
    $time -= $HR if $test[2] != $_[2];
    $time;
}
sub cheat {
    $year = $_[5];
    $month = $_[4];
    die "Month out of range 0..11 in timelocal.pl\n" 
	if $month > 11 || $month < 0;
    die "Day out of range 1..31 in timelocal.pl\n" 
	if $_[3] > 31 || $_[3] < 1;
    die "Hour out of range 0..23 in timelocal.pl\n"
	if $_[2] > 23 || $_[2] < 0;
    die "Minute out of range 0..59 in timelocal.pl\n"
	if $_[1] > 59 || $_[1] < 0;
    die "Second out of range 0..59 in timelocal.pl\n"
	if $_[0] > 59 || $_[0] < 0;
    $guess = $^T;
    @g = gmtime($guess);
    $year += $YearFix if $year < $epoch[5];
    $lastguess = "";
    while ($diff = $year - $g[5]) {
	$guess += $diff * (363 * $DAYS);
	@g = gmtime($guess);
	if (($thisguess = "@g") eq $lastguess){
	    return -1; #date beyond this machine's integer limit
	}
	$lastguess = $thisguess;
    }
    while ($diff = $month - $g[4]) {
	$guess += $diff * (27 * $DAYS);
	@g = gmtime($guess);
	if (($thisguess = "@g") eq $lastguess){
	    return -1; #date beyond this machine's integer limit
	}
	$lastguess = $thisguess;
    }
    @gfake = gmtime($guess-1); #still being sceptic
    if ("@gfake" eq $lastguess){
	return -1; #date beyond this machine's integer limit
    }
    $g[3]--;
    $guess -= $g[0] * $SEC + $g[1] * $MIN + $g[2] * $HR + $g[3] * $DAYS;
    $cheat{$ym} = $guess;
}


1;

