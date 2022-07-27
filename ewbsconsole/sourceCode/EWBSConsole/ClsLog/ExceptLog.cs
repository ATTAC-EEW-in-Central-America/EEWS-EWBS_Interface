using System;
using System.IO;

namespace Apl
{
    namespace Log
    {
        /// <summary>
        /// ExceptLog class
        /// </summary>
        public class ExceptLog
        {
            #region ExceptLog class
            /// <summary>
            /// Start collecting exception logs
            /// </summary>
            /// <param name="pathFileName">Exception log path file name</param>
            /// <param name="saveLogNum">Save exception log files number</param>
            public static void StartExceptLogCollect(string pathFileName, int saveLogNum)
            {
                
                try
                {
                    // Exception log generation management
                    string path = Path.GetDirectoryName(pathFileName);
                    string extn = Path.GetExtension(pathFileName);
                    string[] files = Directory.GetFiles(path, "*" + extn, SearchOption.AllDirectories);
                    if (files.Length > saveLogNum)
                    {
                        for (int i = saveLogNum; i < files.Length; i++)
                            File.Delete(files[i - saveLogNum]);
                    }

                    // Start collecting exception logs
                    StreamWriter sw = new StreamWriter(pathFileName, false, System.Text.Encoding.UTF8);
                    sw.AutoFlush = true;
                    TextWriter tw = TextWriter.Synchronized(sw);
                    Console.SetOut(tw);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    //Console.WriteLine(ex.StackTrace);
                }
                finally
                {
                }
            }
            #endregion
        }
    }
}
