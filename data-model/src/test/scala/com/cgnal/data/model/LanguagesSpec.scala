package com.cgnal.data.model

import org.scalatest.FunSuite

final class LanguagesSpec
  extends FunSuite {

  import Languages._

  test("string to language: italian") {
    val language1: String = stringToLanguage("it-IT")
    assertResult(Italian)(language1)
  }

  test("string to language: english") {

    val language1: String = stringToLanguage("en")
    assertResult(English)(language1)
  }

  test("string to language: english american") {
    val language1: String = stringToLanguage("en-US")
    assertResult(English)(language1)
  }

}
