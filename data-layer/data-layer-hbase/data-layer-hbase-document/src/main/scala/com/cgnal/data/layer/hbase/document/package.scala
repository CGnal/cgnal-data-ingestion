package com.cgnal.data.layer.hbase

import java.sql.Timestamp
import java.time._

import java.time.LocalDate._

import com.cgnal.data.layer.hbase.core._
import com.cgnal.data.model._
import org.apache.hadoop.hbase.util.Bytes

package object document {

  import Bytes._

  type Serializer = (String => Array[Byte], Array[Byte])

  /**
    * Internal Hbase representation, compatible with the corresponding Spark types.
    * Dates are stored internally as the number of days since the Unix epoch (1970-01-01).
    * Timestamps are stored internally as number of micros since epoch.
    */
  type SQLDate = Int
  type SQLTimestamp = Long


  final val MicrosPerSecond: SQLTimestamp = 1000L * 1000L

  /**
    * Returns a java.sql.Timestamp from number of micros since epoch.
    */
  def toJavaTimestamp(us: SQLTimestamp): Timestamp = {
    // setNanos() will overwrite the millisecond part, so the milliseconds should be
    // cut off at seconds
    var seconds = us / MicrosPerSecond
    var micros = us % MicrosPerSecond
    // setNanos() can not accept negative value
    if (micros < 0) {
      micros += MicrosPerSecond
      seconds -= 1
    }
    val t = new Timestamp(seconds * 1000)
    t.setNanos(micros.toInt * 1000)
    t
  }

  /**
    * Returns the number of micros since epoch from java.sql.Timestamp.
    */
  def fromJavaTimestamp(t: Timestamp): SQLTimestamp = {
    if (t != null) {
      t.getTime * 1000L + (t.getNanos.toLong / 1000) % 1000L
    } else {
      0L
    }
  }

  def javaDateAsLocalDate(date: java.util.Date): LocalDate =
    Instant.ofEpochMilli(date.getTime).atZone(ZoneId.systemDefault()).toLocalDate

  def fromLocalDateTime(t: LocalDateTime): SQLTimestamp =
    fromJavaTimestamp(Timestamp.valueOf(t))

  def toLocalDateTime(us: SQLTimestamp): LocalDateTime =
    LocalDateTime.ofInstant(toJavaTimestamp(us).toInstant, ZoneOffset.ofHours(0))


  val reducer: Reducer[Serializer] = Reducer(
    forInt     = i => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}i") }: String => Raw, toBytes(i)),
    forLong    = l => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}l") }: String => Raw, toBytes(l)),
    forFloat   = f => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}f") }: String => Raw, toBytes(f)),
    forDouble  = d => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}d") }: String => Raw, toBytes(d)),
    forBoolean = b => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}b") }: String => Raw, toBytes(b)),
    forString  = s => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}s") }: String => Raw, toBytes(s)),
    forDate    = v => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}v") }: String => Raw, toBytes(v.toEpochDay)),
    forTime    = t => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}t") }: String => Raw, toBytes(fromLocalDateTime(t))),
    forList    = a => ( { key => toBytes(s"$key${DocumentDAO.typeSeparator}a") }: String => Raw, Array.empty[Byte]),
    default    = () => ( { key => Array.empty[Byte] }: String => Raw, Array.empty[Byte])
  )


  val types: Map[Char, Raw => DocumentProperty] = Map(
    'i' -> (b => Bytes.toInt(b)),
    'l' -> (b => Bytes.toLong(b)),
    'f' -> (b => Bytes.toFloat(b)),
    'd' -> (b => Bytes.toDouble(b)),
    'b' -> (b => Bytes.toBoolean(b)),
    's' -> (b => Bytes.toString(b)),
    'v' -> (b => ofEpochDay(toLong(b))),
    't' -> (b => toLocalDateTime(toLong(b))),
    'a' -> (b => List.empty)
  )

}
