local oil    = require "oil"
local oo     = require "loop.base"
local print  = print
local rawget = rawget
local assert = assert
local type   = type
local ipairs = ipairs

require "logging.console"

local Viewer = require "loop.debug.Viewer"
local logger = logging.console()
local view = Viewer()

module("resourceinstance", oo.class)

--- LOOP Class Instance 
function __init(self, instance_data)

	logger:info("In Instance:__init(self, instance_data)")
	logger:info("Printing self:")
	--view:print(self) -- no recommended
	logger:info("Printing instance_data: ")
	view:print(instance_data)

	-- local inst = oo.rawnew(self, instance_data) -- LOCAL inst
	inst = oo.rawnew(self, instance_data)
	inst.instance_id	= rawget(instance_data, "instance_id") or nil
	inst.instance_data	= rawget(instance_data, "instance_data") or {}

	-- Initializing broker
	if inst.broker == nil then inst.broker = init_broker() end

	--[[	
	orb = oil.init()
	orb:loadidlfile("resource_manager.idl")
	inst.engine = orb:newproxy(assert(oil.readfrom("ref.ior")))
	inst.image  = orb:newproxy(assert(oil.readfrom("ref2.ior")))
	]]--	
	
	logger:info("Printing inst ( __init(self, instance_data ): ")
	view:print(inst)
	return inst
end

function get_typevm_zones(self)
	logger:info("In get_availability_zones")
	typevms = inst.zone:get_typevm_zones()
	logger:debug("Types of vms: ", typevms)
	return typevms
end

-- Getting zone detailed
function get_typevm(self, typevm)
	logger:info("In get_typevm()")
	logger:debug("Request typevm: "  .. typevm)
	--typevms = self.get_typevm_zones()
	typevms = inst.zone:get_typevm_zones()
	logger:debug("Printing data of type: " .. type(typevm))
	
	-- TODO: refine
	logger:debug("typevms: " .. type(typevms) )
	logger:info("Printing all typevms: ")
	view:print(typevms)
	logger:info("Printing typevms[typevm]: ")

	view:print( typevms[1] )
	--logger:debug("typevms[type]: " .. typevms)

	logger:info("Iterating typevms")
	for i,vm in ipairs(typevms) do
		view:print(vm)
		if vm.name==typevm then
			logger:info("typevm founded")
			return vm.values
		end
	end	

	return "no founded"
end


--- Adapt InstanceData to HostDescription(machine0)
-- HostDescription	= {cpu, mem, os, arch, bandwith} --VM Instance
-- PhysicalResources	= {name, ip, port, resources(HostDescriptions), languages(List)}
function adapt_idata_host_data(self, instance)

	logger:info("In adapt_idata_host_data")
	logger:info("------------------------")
	logger:info("Printing Engine from adapt_idata_host_data()")
	view:print(instance.engine)
	logger:info("adapt_idata_host_data(instance)")
	view:print(instance.instance_data)

	logger:debug("Printing self.instance_id: " .. instance.instance_id)
	--view:print(self.instance)

	logger:info("Loading Host Parameters")
	host = {}
	host.name	= instance.instance_id or "generic-name"
	host.ip		= instance.instance_data["public_dns_name"] or "139.82.2.1"
	host.port	= "1000"
	host.languages 	= {"lua", "java"} -- TODO: Load from a XML File from Cloud

	host.instance_type =  instance.instance_data["instance_type"] or "vm-unkown"
	
	local image_id = instance.instance_data["image_id"] or "emi-XXXXXX"
	logger:debug("The image id associated is: " .. image_id)
	
	--image_info = instance.image:get_emi_info(image_id) -- OK method 1
	image_info = inst.image:get_emi_info(image_id)
	logger:info("The image_info is:")
	view:print(image_info)
	
	logger:info("For example, the image_info.self.architecture is: " .. image_info.image_data["architecture"])

	-- instance_type
	logger:debug("Type of Instance: " .. host.instance_type)
	logger:info("=========================?>")
	instance_typevm  = self.get_typevm(self, host.instance_type) -- TODO: probably bug	
	--instance_typevm  = self.get_typevm(host.instance_type, host.instance_type)
	logger:info("Printing the instance_type")
	
	view:print(instance_typevm)
	
	cpu = instance_typevm[4].value
	mem = instance_typevm[3].value
	logger:debug("cpu: " .. cpu)
	logger:debug("mem: " .. mem)

	-- host.resources
	host.resources  = {	
				cpu = cpu,	-- instance_type --> availavility_resources.get_details("m1.small")
				mem = mem,	-- 
				os  = "Linux",  -- TODO: Searching some way to get the OS-system
				arch= "Linux_" .. image_info.image_data["architecture"],
				bandwidth = "1000", 
			  }
	return host
end

function get_instances(self, num_instances)
	logger:info("In get_instances()( file resourceinstance.lua )")
	instances = inst.engine:get_instances(num_instances, {}, {})
	--instances = instance.engine:get_instances(1, {}, {})
	--instances = self.engine:get_instances(1, {}, {})
	-- Or: 
	return instances	
end

--[[
-- Getting zone detailed
function get_typevm(self, typevm)
	logger:info("In get_typevm()")
	logger:debug("Request typevm: "  .. typevm)
	--typevms = self.get_typevm_zones()
	typevms = inst.zone:get_typevm_zones()
	logger:debug("Printing data of type: " .. type(typevm))
	
	-- TODO: refine
	logger:debug("typevms: " .. type(typevms) )
	logger:info("Printing all typevms: ")
	view:print(typevms)
	logger:info("Printing typevms[typevm]: ")

	view:print( typevms[1] )
	--logger:debug("typevms[type]: " .. typevms)

	logger:info("Iterating typevms")
	for i,vm in ipairs(typevms) do
		view:print(vm)
		if vm.name==typevm then
			logger:info("typevm founded")
			return vm.values
		end
	end	

	return "no founded"
end
]]--

--[[
function get_typevm_zones(self)
	logger:info("In get_availability_zones")
	typevms = inst.zone:get_typevm_zones()
	logger:debug("Types of vms: ", typevms)
	return typevms
end
]]--

function get_zones(self)
	logger:info("In get_zones()")
	zones = inst.zone:get_zones()
	return zones
end

function init_broker()
	orb = oil.init()
	orb:loadidlfile("resource_manager.idl")
	inst.engine = orb:newproxy(assert(oil.readfrom("ref.ior")))
	inst.image  = orb:newproxy(assert(oil.readfrom("ref2.ior")))
	inst.zone   = orb:newproxy(assert(oil.readfrom("ref3.ior")))
	return true
end

