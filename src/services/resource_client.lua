require "oil"
require "logging.console"
local Instance = require "resourceinstance"

local oo = require "loop.base"
local Viewer = require "loop.debug.Viewer"
local logger = logging.console()
view = Viewer()

oil.main(function()

	logger:info("In function oil.main: ")
	--oil.verbose:level(5)
	orb = oil.init()
	orb:loadidlfile("resource_manager.idl")
	
	-- Only for a simple test
	instance_data = {
		image_id	 = "emi-01FD1576",
		public_dns_name	 = "139.82.2.179",
		private_dns_name = "139.82.2.179",
		state		 = "running",
		key_name	 = "mykey",
		ami_launch_index = "0",
		product_codes	 = "unknow",
		instance_type	 = "m1.small",
		launch_time	 = "2011-03-17T19:31:46.003Z",
		placement	 = "clusterpituba",
		kernel		 = "eki-48261651",
		ramdisk		 = "eri-AB77179D",
	}

	local instance = Instance{
		instance_id = "i-54251318",
		instance_data = instance_data,
	}
	
	local instance_cloud = Instance{}
	
	
	logger:info("Evaluating Functions with Demo Data")
	logger:info("-----------------------------------")
	-- Demo Data
	table_data = Instance:adapt_idata_host_data(instance)
	--table_data = instance_cloud:adapt_idata_host_data(instance) --Review
	logger:info("Printing the table_data")
	view:print(table_data)
		
		
	logger:info("Getting instances")
	instance_data_euca = instance_cloud:get_instances(1)
	view:print(instance_data_euca)

	
	logger:info("Getting Availability Zones")
	zones_data = instance_cloud:get_zones()
	view:print(zones_data)	
	
	logger:info("Getting all typevm")
	typevms = instance_cloud:get_typevm_zones()
	print("typevm_detail: ", typevms)
	view:print(typevms)
	
	
	logger:info("Getting a m1.small type")
	type_vm="m1.small"
	typevm_detail = instance_cloud:get_typevm(type_vm)
	print("type m1.small: ", typevm_detail)
	logger:info("Printing a table typevm details")
	view:print(typevm_detail)
	print(typevm_detail[1].value)	--disk
	print(typevm_detail[2].value)	--max
	print(typevm_detail[3].value)	--ram
	print(typevm_detail[4].value)	--cpu
	print(typevm_detail[5].value)	--free	
	
	-- Get InstanceInfo for each instance
	logger:info("LOADING DATA FROM EUCALYPTUS")
	logger:info("----------------------------")

	-- Printing the instance_info from instance_data_euca
	count = 0
	for _,instance in ipairs(instance_data_euca) do
		instance_info = Instance:adapt_idata_host_data(instance)
		logger:info("Printing Instace_info from: " .. instance_info.name)
		view:print(instance_info)
		count = count + 1
	end
	logger:info("Total number of instances are: " .. count)
	
	
end)

