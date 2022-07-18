package info.vizierdb.commands

import org.specs2.mutable.Specification
import org.specs2.specification.BeforeAll
import info.vizierdb.test.SharedTestResources
import info.vizierdb.calculateProvenance

class PythonProcessProvenance
  extends Specification
  with BeforeAll
{
  def beforeAll = SharedTestResources.init
  def src = "x = 1; y=1; y=y+2; x = y+5"
  val prov = new calculateProvenance()
  val output = prov.calculateProvenance(src)  
  val input_prov = output._1.as[Vector[String]]
  val output_prov = output._2.as[Vector[String]]
  print(output_prov)
  print(input_prov)
  input_prov must contain ('x')
  output_prov must contain ('y')
}
