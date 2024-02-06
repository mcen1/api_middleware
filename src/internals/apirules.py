from internals.awxlauncher import *
apikeyrelationships={'sme':['sme automation','sme-dev'],'itcc':['itcc automation'],'windows':['windows automation'],'network':['network automation'],'linux':['linux automation'],'storage':['storage automation'],'sapbasis':['sap basis automation'],'pha': ['pha automation'], 'abds': ['ab data streaming automation']}
def evaluateRulesValidityOnly(apikeytouse):
  if apikeytouse.startswith('team'):
    return "OK"
  for keycheck in apikeyrelationships:
    if apikeytouse.startswith(keycheck.lower()):
      return "OK"
  return "API key is not valid."

def evaluateRules(apikeytouse,jobname,jobtype):
  if apikeytouse.startswith('team'):
    return "OK"
  if jobtype=="jobname":
    # ServiceNow can run any job with snow in its title
    if apikeytouse.startswith('servicenow'):
      if "snow" not in jobname.lower():
        return "Cannot run a job that isn't for SNOW."
      else:
        return "OK"
  # Begin checks for org-specific
    orgID=getJobOrgByName(jobname,"job_templates")
  if jobtype=="jobid":
    if apikeytouse.startswith('servicenow'):
      if "snow" not in getJobNameByID(jobname).lower():
        return "Cannot look at a job that isn't for SNOW."
      else:
        return "OK"
    orgID=getJobOrgByName(jobname,"jobs")
  print(f"orgID is {orgID}")
  orgname=getOrgNameByID(orgID)
  print(f"Validating if job template named {jobname} is in AWX org {orgname}")
  print(f"orgname is {orgname}")
  for keycheck in apikeyrelationships:
    if apikeytouse.startswith(keycheck.lower()):
      print(f"orgname is {orgname}")
      if  orgname.lower() in apikeyrelationships[keycheck]:
        print(f"Found {orgname} in api keys! Sending OK")
        return "OK"
  print("no key found. giving up!")
  return "Cannot run a job that isn't in the AWX org the API key is tied to. Check if teampi_user has execute access to the job and if it has read access to the AWX org containing the job."

