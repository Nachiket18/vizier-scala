package info.vizierdb

import me.shadaj.scalapy.py
import me.shadaj.scalapy.py.SeqConverters


class calculateProvenance {
    //val listLengthPython = py.Dynamic.global.len(List(1, 2, 3).toPythonProxy)

    def calculateProvenance(src : String) : (me.shadaj.scalapy.py.Dynamic, me.shadaj.scalapy.py.Dynamic) = {

        val ast_parse = py.module("ProcessCellProvenance.ProcessCellProvenance")

        val process_cell = ast_parse.ProcessCellProvenance()
        process_cell.processProvenance(src)

        val output_provenance = process_cell.display_output_provenance()
        val input_provenance = process_cell.display_input_provenance()
        val output = (input_provenance,output_provenance)
        return output 
    }

}

object calProvenance {
    def main(args: Array[String]) = {
        println("Hello, world")
        def src = "x = 1; y=1; y=y+2; x = y+5"
        val prov = new calculateProvenance()
        val output = prov.calculateProvenance(src)
    }
}






