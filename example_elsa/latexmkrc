# Preserve .aux files for cross referencing
# Reference: https://www.overleaf.com/learn/how-to/Cross_referencing_with_the_xr_package_in_Overleaf

add_cus_dep( 'tex', 'aux', 0, 'makeexternaldocument' );
 
sub makeexternaldocument {
    if (!($root_filename eq $_[0]))
    {
        # FOR PDFLATEX
        system( "latexmk -pdf \"$_[0]\"" );
 
        # FOR LATEX+DVIPDF
        # system( "latexmk \"$_[0]\"" );
 
        # FOR XELATEX
        # system( "latexmk -xelatex \"$_[0]\"" );
 
        # FOR LUALATEX
        # system( "latexmk -lualatex \"$_[0]\"" );
   }
}
