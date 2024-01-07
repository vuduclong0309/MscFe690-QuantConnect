/*
* QUANTCONNECT.COM - Equity Transaction Model
* Default Equities Transaction Model
*/

/**********************************************************
* USING NAMESPACES
**********************************************************/
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace QuantConnect.Securities {

    /******************************************************** 
    * QUANTCONNECT PROJECT LIBRARIES
    *********************************************************/
    using QuantConnect.Models;


    /******************************************************** 
    * CLASS DEFINITIONS
    *********************************************************/
    /// <summary>
    /// Default Transaction Model for Equity Security Orders
    /// </summary>
    public class CustomTransactionModel : SecurityTransactionModel {

        /******************************************************** 
        * CLASS PRIVATE VARIABLES
        *********************************************************/


        /******************************************************** 
        * CLASS PUBLIC VARIABLES
        *********************************************************/

        /******************************************************** 
        * CLASS CONSTRUCTOR
        *********************************************************/
        /// <summary>
        /// Initialise the Algorithm Transaction Class
        /// </summary>
        public CustomTransactionModel() {

        }

        /******************************************************** 
        * CLASS PROPERTIES
        *********************************************************/

        /// <summary>
        /// Get the Slippage approximation for this order:
        /// </summary>
        public override decimal GetSlippageApproximation(Security security, Order order) {
            return 0.15m;
        }

    } // End Algorithm Transaction Filling Classes

} // End QC Namespace