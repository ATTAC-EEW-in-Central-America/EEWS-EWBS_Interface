using System.IO;

namespace EWBSConsole.ClsLog
{
    public class LogCustom
    {

        public static void AlternativeLog(string fecha_format,string pathFileName, string msg,string timespan="")
        {
            StreamWriter w = null;

            if (!File.Exists(pathFileName))
            {
                w = new StreamWriter(pathFileName);
            }
            else
            {
                w = File.AppendText(pathFileName);
            }
            //2021-03-17 SE AGREGA MILISEGUNDOS
            //2021-03-19 SE AGREGA TIMESPAN DIFF
            w.WriteLine(fecha_format+ ": " + msg + (string.IsNullOrWhiteSpace(timespan) ? "" : " | Timespan diff: " + timespan));
            w.Close();

        }
    }
}
