I recently stumbled across the Palo Alto Police Department's daily police report logs online, which they conveniently publish as PDF files (https://www.cityofpaloalto.org/Departments/Police/Public-Information-Portal/Police-Report-Log). My initial thought was simple: parse these PDFs, extract the data, and organize it neatly into a database. Easy, right?

Turns out, parsing PDF files—especially those containing tables—is deceptively tricky. PDF files don't inherently preserve table structures, and these specific reports were particularly challenging. The data tables spanned multiple pages, breaking apart in unexpected places. This meant I had to recombine fragments carefully to reconstruct coherent tables.

After experimenting with various tools and approaches, I settled on Python combined with Tabula, which allowed me to reliably extract and reconstruct the table data.

Wanting to experiment a bit further, I decided to build a quick frontend to showcase the data visually. I've been meaning to explore Next.js deployed on Vercel, and this seemed like a perfect opportunity. The result? A simple, single-page website featuring an interactive table and map to visualize the police report data effectively.

You can check out the full codebase and my approach on GitHub: https://github.com/brianhama/palo-alto-police-case-reports.

The script for parsing the pdfs is located in the script folder.

The live website is https://www.paloaltopolice.org/