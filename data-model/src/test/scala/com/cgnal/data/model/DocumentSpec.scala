package com.cgnal.data.model

import org.scalatest.FunSuite

final class DocumentSpec
  extends FunSuite {

  private val bytes: Array[Byte] = Array[Byte]()

  test("testing withProperty") {

    val doc = Document(id = "",
      properties = Map[String, DocumentProperty](
        "Text" -> "ciao"
      ),
      body = DocumentBody(None, bytes)
    )

    val expected = Document(id = "",
      properties = Map[String, DocumentProperty](
        "Text" -> "arrivederci"
      ),
      body = DocumentBody(None, bytes)
    )

    val withProperty: Document = doc.withProperty("Text","arrivederci")

    assertResult(expected.properties )(withProperty.properties)
  }

  test("testing withMimeType") {
    val doc = Document(id = "",
      properties = Map[String, DocumentProperty](
        "Text" -> "ciao"
      ),
      body = DocumentBody(None, bytes)
    )

    val docWIthMimeType: Document = doc.withMimeType(MimeTypes.textPlain)

    val expected =  Document(id = "",
      properties = Map[String, DocumentProperty](
        "Text" -> "ciao"
      ),
      body = DocumentBody(Some(MimeTypes.textPlain), bytes))

    assertResult(expected )(docWIthMimeType)

    val primaryType: String = MimeTypes.textPlain.primary
    val subType: String = MimeTypes.textPlain.secondary

    assertResult("text" )(primaryType)
    assertResult("plain" )(subType)

  }

  /*
  test("testing stringToMimeType") {
    val mimeType: Option[MimeTypes] = stringToMimeType("text/plain")
    assertResult(true)(mimeType.isDefined)
    assertResult(Some(new MimeTypes("text","plain").toValue))(mimeType.map(_.toValue))
  }
  */

}
