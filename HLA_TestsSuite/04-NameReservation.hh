#ifndef FED_EXECUTION_TEST_H
#define FED_EXECUTION_TEST_H

#include <RTI/NullFederateAmbassador.h>

namespace rti1516 {
	class RTIambassador;
}

class TestFedAmb : public rti1516::NullFederateAmbassador
{
public:
	TestFedAmb()
		throw ();
	~TestFedAmb()
		throw ();

	int execute(int argc, char **argv);

    virtual
    void
    objectInstanceNameReservationSucceeded(std::wstring const &
                                           theObjectInstanceName)
      throw (rti1516::UnknownName,
             rti1516::FederateInternalError);

    virtual
    void
    objectInstanceNameReservationFailed(std::wstring const &
                                        theObjectInstanceName)
      throw (rti1516::UnknownName,
             rti1516::FederateInternalError);


private:
	rti1516::RTIambassador *rtiAmb;
	rti1516::FederateHandle fedHandle;
	std::wstring fedName;
	std::wstring federationName;

};

#endif // FED_EXECUTION_TEST_H
