package com.cgnal.data

import java.time.{LocalDate, LocalDateTime}

import shapeless.ops.coproduct.Selector
import shapeless.{:+:, CNil, Coproduct}

import scala.language.implicitConversions

package object model {

  type Properties = Map[String, DocumentProperty]

  type DocumentProperty =
      List[String]                             :+:
      Int                                      :+:
      Long                                     :+:
      Float                                    :+:
      Double                                   :+:
      Boolean                                  :+:
      String                                   :+:
      LocalDate                                :+:
      LocalDateTime                            :+:
      CNil

  case class Reducer[A](forInt: Int => A,
                        forLong: Long => A,
                        forFloat: Float => A,
                        forDouble: Double => A,
                        forBoolean: Boolean => A,
                        forString: String => A,
                        forDate: LocalDate => A,
                        forTime: LocalDateTime => A,
                        forList : List[String] => A,
                        default: () => A)

  implicit class RichDocumentProperty(prop: DocumentProperty) {


    def get[A](implicit es: Selector[DocumentProperty, A]): Option[A] = prop.select[A]

    def reduce[B](reducer: Reducer[B]): B =
      get[Int].map                   { reducer.forInt     } orElse
        get[Long].map                { reducer.forLong    } orElse
        get[Float].map               { reducer.forFloat   } orElse
        get[Double].map              { reducer.forDouble  } orElse
        get[Boolean].map             { reducer.forBoolean } orElse
        get[String].map              { reducer.forString  } orElse
        get[LocalDate].map           { reducer.forDate    } orElse
        get[LocalDateTime].map       { reducer.forTime    } orElse
        get[List[String]].map        { reducer.forList    } getOrElse
        reducer.default()
  }


  implicit def Int2Prop(p: Int): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Long2Prop(p: Long): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Float2Prop(p: Float): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Double2Prop(p: Double): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Boolean2Prop(p: Boolean): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def String2Prop(p: String): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Date2Prop(p: LocalDate): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def Time2Prop(p: LocalDateTime): DocumentProperty = Coproduct[DocumentProperty](p)

  implicit def List2Prop(p: List[String]): DocumentProperty = Coproduct[DocumentProperty](p)


  implicit class RichProperties(properties: Properties) {
    def property[A](key: String)(implicit es: Selector[DocumentProperty, A]): Option[A] = properties.get(key).flatMap(_.select)
  }

  /**
    * safely extracts a property out of a map
    */
  def safeGetOrElse[A](documentProperties: Properties, key: String, default: A)(implicit sel: Selector[DocumentProperty, A]): A = {
    documentProperties.get(key) match {
      case Some(p) => p.select[A] match {
        case Some(x) => x
        case None => default
      }
      case None => default
    }
  }

}
