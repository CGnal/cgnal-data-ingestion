package com.cgnal.data.model

object Languages {

  val Danish     = "Danish"
  val German     = "German"
  val Estonian   = "Estonian"
  val Greek      = "Greek"
  val English    = "English"
  val Spanish    = "Spanish"
  val Finnish    = "Finnish"
  val French     = "French"
  val Hungarian  = "Hungarian"
  val Icelandic  = "Icelandic"
  val Italian    = "Italian"
  val Dutch      = "Dutch"
  val Norwegian  = "Norwegian"
  val Polish     = "Polish"
  val Portuguese = "Portuguese"
  val Russian    = "Russian"
  val Swedish    = "Swedish"
  val Thai       = "Thai"
  val Unknown    = "Unknown"

  def stringToLanguage(x: String): String = {

    val stringtoMatch = if(x.matches("[a-z][a-z]-[A-Z][A-Z]")) x.substring(0,2)  else x.toLowerCase()

    stringtoMatch match {
      case "da" => Danish
      case "de" => German
      case "et" => Estonian
      case "el" => Greek
      case "en" => English
      case "es" => Spanish
      case "fi" => Finnish
      case "fr" => French
      case "hu" => Hungarian
      case "is" => Icelandic
      case "it" => Italian
      case "nl" => Dutch
      case "no" => Norwegian
      case "pl" => Polish
      case "pt" => Portuguese
      case "ru" => Russian
      case "sv" => Swedish
      case "th" => Thai
      case _    => Unknown
    }
  }

}
