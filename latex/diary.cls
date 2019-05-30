\LoadClass{article}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diary}[2019/05/30 My custom diary class]
\RequirePackage{titlesec}

\titleformat{\section}         % Customise the \section command
{\Large\scshape\raggedright} % Make the \section headers large (\Large),
% small capitals (\scshape) and left aligned (\raggedright)
{}{0em}                      % Can be used to give a prefix to all sections, like 'Section ...'
{}                           % Can be used to insert code before the heading
[\titlerule]                 % Inserts a horizontal line after the heading


\newcommand{\doubledatedsection}[3]{%
\section[#2]{#1. #2  \hfill #3}%
}
