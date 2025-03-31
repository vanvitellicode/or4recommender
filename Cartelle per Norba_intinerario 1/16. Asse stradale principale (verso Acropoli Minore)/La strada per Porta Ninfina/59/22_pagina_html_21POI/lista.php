<?php
//echo "<style type=\"text/css\">
//.link_text {
//   background:url('../../../demo/tools/link_text.png') 50% 50% no-repeat no-repeat;
//   padding-left: 5px;
//}
//.link_img {
//   background:url('../../../demo/tools/link_img.png') 50% 50% no-repeat no-repeat;
//   padding-left: 5px;
//}
//</style>";
$cartella = opendir('./');
while ($file = readdir($cartella)) {
$file_array[] = $file;
}
echo "<TR><TD><UL>";
foreach ($file_array as $file) {
# se il file inizia con .. lo tralascio
if ( $file == ".." || $file == ".") {
continue;
}
#trovo i file e creo il link

$e=substr(strrchr($file, "."), 0); // prendo l'estensione finale
$i=substr(strstr($file, "."), 0); // prendo l'estensione totale
$nome=basename($file,$i);
$a=""; //sostituisco lo spazio vuoto con il relativo codice html
$b=" ";
$comp_value=strcmp($e, ".html");
$index=strcmp($file, "index.html");
if($index==0)
$comp_value=-1;
if($comp_value==0){
	if (strpos($i,"txt") !== false) {
				  echo "<li><img src=\"../../../demo/upload/tools/link_text.png\" border=0 height=25 width=25/><a target=\"inner_frame\" href=\"$file\" title=\"$nome\" class=\"link_text\"><b>$nome</b></a></li><br>"; //questo crea il link
			  }
			  else {
				  echo "<li><img src=\"../../../demo/upload/tools/link_img.png\" border=0 height=25 width=25/><a target=\"inner_frame\" href=\"$file\" title=\"$nome\" class=\"link_img\"><b>$nome</b></a></li><br>"; //questo crea il link
			  }



}
}
?>
