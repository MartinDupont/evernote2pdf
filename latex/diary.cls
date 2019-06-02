\LoadClass{book}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diary}[2019/05/30 My custom diary class]
\RequirePackage{titlesec}
\usepackage{tocloft}

\setcounter{tocdepth}{4}
\setcounter{secnumdepth}{3}

\setlength{\cftchapindent}{0pt}% Remove indent for \section
\setlength{\cftsecindent}{0pt}% Remove indent for \section
\setlength{\cftsubsecindent}{0pt}% Remove indent for \subsection
\setlength{\cftsubsubsecindent}{0pt}% Remove indent for \section
\addtolength{\cftsubsubsecnumwidth}{20pt}


\titleformat{\subsubsection}         % Customise the \section command
{\Large\scshape\raggedright} % Make the \section headers large (\Large),
% small capitals (\scshape) and left aligned (\raggedright)
{}{0em}                      % Can be used to give a prefix to all sections, like 'Section ...'
{}                           % Can be used to insert code before the heading
[\titlerule]                 % Inserts a horizontal line after the heading


\newcommand{\doubledatedsection}[4]{%
\setcounter{chapter}{#1}
\setcounter{section}{#2}
\setcounter{subsection}{#3}
\subsubsection[#4]{#1.#2.#3 #4}%
}

\newcommand{\doubledatedsectionupdate}[7]{%
\setcounter{chapter}{#1}
\setcounter{section}{#2}
\setcounter{subsection}{#3}
\subsubsection[#7]{#1.#2.#3 #7}%
\begin{flushright} updated: #4.#5.#6 \end{flushright}
}
