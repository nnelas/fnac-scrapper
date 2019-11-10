# fnac-scrapper

Python Application that allows FNAC Pro members to manage their products easily


## Product Requirements

* Platform (FNAC) login
    * `https://secure.fnac.pt/identity/gateway/signin`
* Goto:

1) Inventory
	* `https://mp.fnac.pt/compte/vendeur/inventaire/num_desc/1/10/1`
	* Where:
		* `num_desc` - order  
        * `1` - page number
        * `10` - number of items per page
    * Get:
	    * `Tem X ofertas` - store X
	
2) Open product editor (cannot get direct link)
	* `https://mp.fnac.pt/compte/vendeur/inventaire/editer/D1CEA048-3748-3253-538B-316F1394A6AD/1`
    
3) Open product live (cannot get direct link)
    * `https://www.fnac.pt/mp12050856/Pelicula-Ecra-de-Vidro-Temperado-Lmobile-para-iPhone-Xs-Max`
    * Get:
        * `Todas as ofertas` - store map (`store_name`, `price`, `shipping`)
        * Add `final_price` - that's `price` plus `shipping`
        
4) For every product, whenever `final_price` isn't from `skyhe`, goto 2) and lower it to `best_price - 0.01`
