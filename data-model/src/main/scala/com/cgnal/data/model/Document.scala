package com.cgnal.data.model

import shapeless.ops.coproduct.Selector
import scalaz.syntax.std.option._

case class Document(id: String, properties: Properties, body: DocumentBody){

  def property[A](key: String)(implicit es: Selector[DocumentProperty, A]): Option[A] =  properties.property[A](key)

  def withBlob(blob: Array[Byte]): Document = copy(body = DocumentBody(body.mimeType, blob))

  def withMimeType(mimeType: MimeTypes): Document = copy(body = DocumentBody(mimeType.some , body.blob))

  def withProperty(key: String, property: DocumentProperty) : Document = copy(properties = properties + (key -> property))
}
