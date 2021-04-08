#!/usr/bin/perl

use strict;
use warnings;

#
# insert_file.pl file_to_insert_to file_to_insert line_num_to_insert_at
#

my $file_to_insert_to = $ARGV[0];
my $file_to_insert = $ARGV[1];
my $line_num_to_insert_at = $ARGV[2];

die "Not enough parameters" if @ARGV != 3;

die "file_to_insert_to does not exist" if !-f $file_to_insert_to;
die "file_to_insert does not exist" if !-f $file_to_insert;
die "line_num_to_insert_at is not an integer" if $line_num_to_insert_at !~ m/^[0-9]+/;

# I cannot depend on any CPAN modules being present

sub slurp
{
    my ($file) = @_;

    my @lines;
    my $fh;

    open $fh, '<', $file or die "Cannot open :$file: for slurping";
    while (<$fh>) {
        chomp;
        push (@lines, $_);
    }
    close $fh;

    return @lines;
}

my @file_to_insert_to_lines = slurp ($file_to_insert_to);
my @file_to_insert = slurp ($file_to_insert);
my $num_lines = @file_to_insert_to_lines;

my @output;

# don't freak, I have to do it this way
for (my $i = 0; $i < $num_lines; $i++) {
    if ($i == $line_num_to_insert_at) {
        push (@output, @file_to_insert);
    }
    push (@output, $file_to_insert_to_lines[$i]);
}

my $fh;
open $fh, '>', $file_to_insert_to or die "Cannot open $file_to_insert_to for writing";
foreach my $line (@output) {
    print $fh $line . "\n";
}
close $fh;

