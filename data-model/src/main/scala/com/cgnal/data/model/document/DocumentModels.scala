package com.cgnal.data.model.document

import shapeless.ops.coproduct.Selector

case class MimeType(primary : String, secondary : String)

case class DocumentBody(mimeType: Option[MimeType], blob: Array[Byte])

case class Document(id: String, properties: Properties, body: DocumentBody){

  def property[A](key: String)(implicit es: Selector[DocumentProperty, A]): Option[A] =  properties.property[A](key)

  def withBlob(blob: Array[Byte]): Document = copy(body = DocumentBody(body.mimeType, blob))

  def withMimeType(mimeType: MimeType): Document = copy(body = DocumentBody(Some(mimeType) , body.blob))

  def withProperty(key: String, property: DocumentProperty) : Document = copy(properties = properties + (key -> property))
}
